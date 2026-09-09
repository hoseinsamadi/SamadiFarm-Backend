"""
Django settings for the Samadi Farm backend project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local development secrets without adding a dotenv runtime dependency.
local_env = BASE_DIR / ".env"
if local_env.exists():
    for line in local_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

# SECURITY WARNING: keep the secret key used in production secret!
# در محیط production حتماً یک متغیر محیطی DJANGO_SECRET_KEY تنظیم کنید.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-this-key-before-deploying-to-production",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback/")
SMS_IR_API_KEY = os.environ.get("SMS_IR_API_KEY", "")
SMS_IR_TEMPLATE_ID = os.environ.get("SMS_IR_TEMPLATE_ID", "")
SMS_IR_VERIFY_URL = os.environ.get("SMS_IR_VERIFY_URL", "https://api.sms.ir/v1/send/verify")
OTP_TTL_SECONDS = 120
SMS_IR_SANDBOX = os.environ.get("SMS_IR_SANDBOX", "False").lower() == "true"
SMS_IR_TEST_CODE = os.environ.get("SMS_IR_TEST_CODE", "12345")
CRYPTO_NETWORK = os.environ.get("CRYPTO_NETWORK", "Ethereum (ERC20)")
CRYPTO_SYMBOL = os.environ.get("CRYPTO_SYMBOL", "USDT")
CRYPTO_WALLET_ADDRESS = os.environ.get("CRYPTO_WALLET_ADDRESS", "")
CRYPTO_USDT_CONTRACT = os.environ.get("CRYPTO_USDT_CONTRACT", "")
CRYPTO_USDT_RATE_TOMAN = os.environ.get("CRYPTO_USDT_RATE_TOMAN", "229000")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "corsheaders",
    # local apps
    "products",
    "posts.apps.PostsConfig",
    "reviews.apps.ReviewsConfig",
    "payments.apps.PaymentsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # باید قبل از CommonMiddleware باشد
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# فعلاً SQLite — همان چیزی که خواسته بودید. اگر بعداً خواستید به Postgres مهاجرت کنید
# فقط کافی‌ست این بخش را عوض کنید، بقیه‌ی کد دست‌نخورده می‌ماند.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# CORS — در توسعه به فرانت Next.js روی لوکال‌هاست اجازه می‌دهیم.
# برای production حتماً دامنه‌ی واقعی فرانت را جایگزین کنید.
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True
