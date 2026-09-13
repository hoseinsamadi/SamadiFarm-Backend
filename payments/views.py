import json
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from products.models import Product

from .models import PaymentTransaction


def _zarinpal_post(url, payload):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ValueError("ارتباط با زرین‌پال برقرار نشد.") from error


def _zarinpal_result_redirect(status, **params):
    query = urlencode({"status": status, **params})
    return HttpResponseRedirect(f"{settings.FRONTEND_URL.rstrip('/')}/payment/result?{query}")


def _validated_order_items(raw_items):
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("سبد خرید خالی یا نامعتبر است.")

    quantities = {}
    for item in raw_items:
        if not isinstance(item, dict) or not item.get("id"):
            raise ValueError("اطلاعات یکی از محصولات نامعتبر است.")
        try:
            quantity = int(item.get("qty", 0))
        except (TypeError, ValueError):
            raise ValueError("تعداد محصول نامعتبر است.")
        if quantity < 1:
            raise ValueError("تعداد محصول باید حداقل یک باشد.")
        slug = str(item["id"])
        quantities[slug] = quantities.get(slug, 0) + quantity

    products = {
        product.slug: product
        for product in Product.objects.filter(slug__in=quantities, is_active=True)
    }
    if len(products) != len(quantities):
        raise ValueError("یک یا چند محصول دیگر قابل خرید نیستند.")

    items = []
    amount = Decimal("0")
    for slug, quantity in quantities.items():
        product = products[slug]
        if product.stock < quantity:
            raise ValueError(f"موجودی «{product.name}» کافی نیست.")
        items.append({"id": slug, "name": product.name, "qty": quantity, "price": product.price})
        amount += Decimal(product.price) * quantity
    return items, amount


@csrf_exempt
@login_required
@require_POST
def submit_crypto_transaction(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "بدنه درخواست معتبر نیست."}, status=400)

    try:
        amount_toman = Decimal(str(payload.get("amount_toman", 0)))
        rate_toman = Decimal(settings.CRYPTO_USDT_RATE_TOMAN)
        amount = (amount_toman / rate_toman).quantize(Decimal("0.000001"))
    except (InvalidOperation, TypeError, ValueError):
        amount_toman = Decimal("0")
        amount = Decimal("0")
    if amount_toman <= 0 or amount <= 0:
        return JsonResponse({"detail": "مبلغ تراکنش باید بیشتر از صفر باشد."}, status=400)

    user = request.user
    transaction = PaymentTransaction.objects.create(
        user=user,
        customer_name=user.get_full_name(),
        customer_email=user.email,
        customer_phone=user.username if user.username.startswith("09") else "",
        amount=amount,
        currency=payload.get("currency", "USDT"),
        method=PaymentTransaction.Method.CRYPTO,
        transaction_hash=str(payload.get("transaction_hash", "")).strip(),
        network=settings.CRYPTO_NETWORK,
        wallet_address=settings.CRYPTO_WALLET_ADDRESS,
        items=payload.get("items", []),
        shipping_address=payload.get("shipping_address", {}),
    )
    return JsonResponse({"ok": True, "transaction_id": transaction.pk, "status": transaction.status}, status=201)


@csrf_exempt
@login_required
@require_POST
def zarinpal_create(request):
    if not settings.ZARINPAL_MERCHANT_ID:
        return JsonResponse({"detail": "شناسهٔ پذیرندهٔ زرین‌پال در تنظیمات سرور وارد نشده است."}, status=503)

    try:
        payload = json.loads(request.body or "{}")
        items, amount = _validated_order_items(payload.get("items"))
    except (json.JSONDecodeError, ValueError) as error:
        return JsonResponse({"detail": str(error)}, status=400)

    user = request.user
    transaction = PaymentTransaction.objects.create(
        user=user,
        customer_name=user.get_full_name(),
        customer_email=user.email,
        customer_phone=user.username if user.username.startswith("09") else "",
        amount=amount,
        currency="IRT",
        method=PaymentTransaction.Method.ZARINPAL,
        items=items,
        shipping_address=payload.get("shipping_address", {}),
    )
    request_payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(amount),
        "currency": "IRT",
        "callback_url": settings.ZARINPAL_CALLBACK_URL,
        "description": f"سفارش شماره {transaction.pk} صمدی فارم",
        "metadata": {"order_id": str(transaction.pk)},
    }
    if transaction.customer_phone:
        request_payload["metadata"]["mobile"] = transaction.customer_phone
    if transaction.customer_email:
        request_payload["metadata"]["email"] = transaction.customer_email

    try:
        response = _zarinpal_post(settings.ZARINPAL_REQUEST_URL, request_payload)
        data = response.get("data") or {}
        authority = data.get("authority")
        if data.get("code") != 100 or not authority:
            transaction.status = PaymentTransaction.Status.FAILED
            transaction.note = str((response.get("errors") or [{"message": "خطا در ایجاد درخواست پرداخت"}])[0].get("message", ""))
            transaction.save(update_fields=["status", "note"])
            return JsonResponse({"detail": "ایجاد درخواست پرداخت در زرین‌پال ناموفق بود."}, status=502)
    except ValueError as error:
        transaction.status = PaymentTransaction.Status.FAILED
        transaction.note = str(error)
        transaction.save(update_fields=["status", "note"])
        return JsonResponse({"detail": str(error)}, status=502)

    transaction.authority = authority
    transaction.save(update_fields=["authority"])
    return JsonResponse({
        "transaction_id": transaction.pk,
        "payment_url": f"{settings.ZARINPAL_START_PAY_URL}{authority}",
    }, status=201)


@require_GET
def zarinpal_callback(request):
    authority = request.GET.get("Authority", "").strip()
    transaction = PaymentTransaction.objects.filter(
        method=PaymentTransaction.Method.ZARINPAL, authority=authority
    ).first()
    if not transaction:
        return _zarinpal_result_redirect("failed")
    if request.GET.get("Status") != "OK":
        transaction.status = PaymentTransaction.Status.FAILED
        transaction.note = "پرداخت توسط کاربر لغو شد یا ناموفق بود."
        transaction.save(update_fields=["status", "note"])
        return _zarinpal_result_redirect("failed", order_id=transaction.pk)

    try:
        response = _zarinpal_post(settings.ZARINPAL_VERIFY_URL, {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(transaction.amount),
            "authority": authority,
        })
        data = response.get("data") or {}
        if data.get("code") not in (100, 101):
            raise ValueError("اعتبارسنجی پرداخت ناموفق بود.")
    except ValueError as error:
        transaction.status = PaymentTransaction.Status.FAILED
        transaction.note = str(error)
        transaction.save(update_fields=["status", "note"])
        return _zarinpal_result_redirect("failed", order_id=transaction.pk)

    transaction.status = PaymentTransaction.Status.PAID
    transaction.transaction_hash = str(data.get("ref_id", transaction.transaction_hash))
    transaction.paid_at = transaction.paid_at or timezone.now()
    transaction.note = "پرداخت زرین‌پال تأیید شد."
    transaction.save(update_fields=["status", "transaction_hash", "paid_at", "note"])
    return _zarinpal_result_redirect("success", order_id=transaction.pk, ref_id=transaction.transaction_hash)


@login_required
@require_GET
def my_orders(request):
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by("-created_at")
    return JsonResponse({
        "orders": [
            {
                "id": transaction.id,
                "amount": str(transaction.amount),
                "currency": transaction.currency,
                "payment_status": transaction.status,
                "payment_status_label": transaction.get_status_display(),
                "order_status": transaction.order_status,
                "order_status_label": transaction.get_order_status_display(),
                "method_label": transaction.get_method_display(),
                "transaction_hash": transaction.transaction_hash,
                "items": transaction.items,
                "created_at": transaction.created_at.isoformat(),
                "paid_at": transaction.paid_at.isoformat() if transaction.paid_at else None,
            }
            for transaction in transactions
        ]
    })
