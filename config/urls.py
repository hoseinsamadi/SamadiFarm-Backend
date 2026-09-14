from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .auth_views import current_user, google_callback, google_start, login_user, logout_user, update_profile
from .crypto_views import crypto_info, crypto_quote
from .otp_views import send_otp, verify_otp
from payments.views import my_orders, payment_methods, submit_card_to_card_transaction, submit_crypto_transaction, zarinpal_callback, zarinpal_create

urlpatterns = [
    path(f"{getattr(settings, 'ADMIN_URL', 'admin')}/", admin.site.urls),
    path("api/", include("products.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("reviews.urls")),
    path("api/auth/google/", google_start, name="google-start"),
    path("api/auth/google/callback/", google_callback, name="google-callback"),
    path("api/auth/me", current_user, name="current-user"),
    path("api/auth/profile", update_profile, name="update-profile"),
    path("api/auth/login", login_user, name="login-user"),
    path("api/auth/logout", logout_user, name="logout-user"),
    path("api/auth/send-otp", send_otp, name="send-otp"),
    path("api/auth/verify-otp", verify_otp, name="verify-otp"),
    path("api/payments/crypto/info", crypto_info, name="crypto-info"),
    path("api/payments/crypto/quote", crypto_quote, name="crypto-quote"),
    path("api/payments/crypto/transactions", submit_crypto_transaction, name="submit-crypto-transaction"),
    path("api/payments/card-to-card/transactions", submit_card_to_card_transaction, name="submit-card-to-card-transaction"),
    path("api/payments/methods", payment_methods, name="payment-methods"),
    path("api/payments/zarinpal/create", zarinpal_create, name="zarinpal-create"),
    path("api/payments/zarinpal/callback", zarinpal_callback, name="zarinpal-callback"),
    path("api/payments/my-orders", my_orders, name="my-orders"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
