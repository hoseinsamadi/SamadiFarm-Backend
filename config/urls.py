from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .auth_views import current_user, google_callback, google_start, logout_user
from .otp_views import send_otp, verify_otp

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("products.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("reviews.urls")),
    path("api/auth/google/", google_start, name="google-start"),
    path("api/auth/google/callback/", google_callback, name="google-callback"),
    path("api/auth/me", current_user, name="current-user"),
    path("api/auth/logout", logout_user, name="logout-user"),
    path("api/auth/send-otp", send_otp, name="send-otp"),
    path("api/auth/verify-otp", verify_otp, name="verify-otp"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
