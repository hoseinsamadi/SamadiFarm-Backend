import hashlib
import json
import secrets
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


def normalize_phone(value):
    translation = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "0123456789" * 2)
    phone = str(value or "").translate(translation).replace(" ", "").replace("-", "")
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("98"):
        phone = "0" + phone[2:]
    elif phone.startswith("9") and len(phone) == 10:
        phone = "0" + phone
    return phone


def _json_response(response):
    return json.loads(response.read().decode("utf-8"))


def _send_sms(phone, code):
    if not settings.SMS_IR_API_KEY or not settings.SMS_IR_TEMPLATE_ID:
        raise RuntimeError("SMS_IR_API_KEY یا SMS_IR_TEMPLATE_ID تنظیم نشده است.")
    payload = json.dumps({
        "mobile": phone,
        "templateId": int(settings.SMS_IR_TEMPLATE_ID),
        "parameters": [{"name": "Code", "value": code}],
    }).encode("utf-8")
    request = Request(
        settings.SMS_IR_VERIFY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "x-api-key": settings.SMS_IR_API_KEY,
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            result = _json_response(response)
    except HTTPError as error:
        try:
            provider_error = json.loads(error.read().decode("utf-8"))
            message = provider_error.get("message") or f"پاسخ ناموفق SMS.ir ({error.code})"
        except (json.JSONDecodeError, UnicodeDecodeError):
            message = f"پاسخ ناموفق SMS.ir ({error.code})"
        raise RuntimeError(f"SMS.ir: {message}") from error
    except (URLError, json.JSONDecodeError) as error:
        raise RuntimeError("ارتباط با سرویس SMS.ir انجام نشد.") from error
    if result.get("status") not in (1, True):
        raise RuntimeError(result.get("message") or "ارسال کد تأیید ناموفق بود.")


@csrf_exempt
@require_POST
def send_otp(request):
    phone = normalize_phone(request.data.get("phone") if hasattr(request, "data") else None)
    if not phone or len(phone) != 11 or not phone.startswith("09"):
        try:
            body = json.loads(request.body or "{}")
            phone = normalize_phone(body.get("phone"))
        except (TypeError, json.JSONDecodeError):
            phone = ""
    if len(phone) != 11 or not phone.startswith("09"):
        return JsonResponse({"detail": "شماره موبایل معتبر نیست."}, status=400)

    code = settings.SMS_IR_TEST_CODE if settings.SMS_IR_SANDBOX else str(secrets.randbelow(90000) + 10000)
    provider_warning = ""
    try:
        _send_sms(phone, code)
    except RuntimeError as error:
        if not settings.SMS_IR_SANDBOX or "قالب یافت نشد" not in str(error):
            return JsonResponse({"detail": str(error)}, status=503)
        provider_warning = str(error)

    request.session["otp_phone"] = phone
    request.session["otp_hash"] = hashlib.sha256(code.encode()).hexdigest()
    request.session["otp_expires_at"] = int(time.time()) + settings.OTP_TTL_SECONDS
    request.session.modified = True
    response = {"ok": True, "message": "کد تأیید Sandbox آماده است."}
    if settings.SMS_IR_SANDBOX:
        response["sandbox_code"] = code
        if provider_warning:
            response["provider_warning"] = provider_warning
    return JsonResponse(response)


@csrf_exempt
@require_POST
def verify_otp(request):
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        body = {}
    phone = normalize_phone(body.get("phone"))
    code = str(body.get("otp") or "").strip()
    session_phone = request.session.get("otp_phone")
    expected_hash = request.session.get("otp_hash")
    expires_at = request.session.get("otp_expires_at", 0)
    if not session_phone or phone != session_phone or not expected_hash or int(time.time()) > int(expires_at):
        return JsonResponse({"detail": "کد تأیید منقضی شده است. دوباره درخواست کد کنید."}, status=400)
    if hashlib.sha256(code.encode()).hexdigest() != expected_hash:
        return JsonResponse({"detail": "کد تأیید صحیح نیست."}, status=400)

    User = get_user_model()
    user, created = User.objects.get_or_create(username=phone, defaults={"first_name": "کاربر"})
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    login(request, user)
    for key in ("otp_phone", "otp_hash", "otp_expires_at"):
        request.session.pop(key, None)
    return JsonResponse({
        "ok": True,
        "created": created,
        "user": {"id": user.id, "name": user.get_full_name() or "کاربر", "phone": phone, "email": user.email or None},
    })
