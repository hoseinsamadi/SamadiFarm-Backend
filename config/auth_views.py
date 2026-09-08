import json
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST


def _frontend_url(path):
    if not path or not path.startswith("/") or path.startswith("//"):
        path = "/account"
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def _google_configured():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


@require_GET
def google_start(request):
    if not _google_configured():
        return JsonResponse({"detail": "Google OAuth is not configured on the server."}, status=503)

    next_path = request.GET.get("next", "/account")
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    request.session["google_oauth_next"] = next_path if next_path.startswith("/") and not next_path.startswith("//") else "/account"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return redirect("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


def _google_json_request(url, data):
    request = Request(url, data=urlencode(data).encode("utf-8"), headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


@require_GET
def google_callback(request):
    state = request.GET.get("state", "")
    expected_state = request.session.pop("google_oauth_state", "")
    next_path = request.session.pop("google_oauth_next", "/account")
    if not state or not expected_state or state != expected_state:
        return redirect(_frontend_url("/login?error=google_state"))
    if request.GET.get("error"):
        return redirect(_frontend_url("/login?error=google_cancelled"))

    try:
        token = _google_json_request("https://oauth2.googleapis.com/token", {
            "code": request.GET.get("code", ""),
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        })
        user_request = Request("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {token['access_token']}"})
        with urlopen(user_request, timeout=15) as response:
            profile = json.loads(response.read().decode("utf-8"))
    except (KeyError, HTTPError, URLError, json.JSONDecodeError):
        return redirect(_frontend_url("/login?error=google_failed"))

    email = profile.get("email", "").strip().lower()
    if not email or not profile.get("email_verified", False):
        return redirect(_frontend_url("/login?error=google_email"))

    User = get_user_model()
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        base_username = f"google_{profile.get('sub', '')}"[:150] or f"google_{secrets.token_hex(8)}"
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username[:140]}_{suffix}"
        user = User(username=username, email=email)
    user.first_name = profile.get("given_name", "")[:150]
    user.last_name = profile.get("family_name", "")[:150]
    user.save()
    login(request, user)
    return redirect(_frontend_url(next_path))


@require_GET
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Authentication required."}, status=401)
    return JsonResponse({
        "id": request.user.id,
        "name": request.user.get_full_name() or request.user.username,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email or None,
        "phone": getattr(request.user, "phone", None),
    })


@require_POST
def logout_user(request):
    logout(request)
    return JsonResponse({"ok": True})
