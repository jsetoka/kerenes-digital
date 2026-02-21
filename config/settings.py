from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # IMPORTANT
load_dotenv(BASE_DIR / ".env")

ENV = os.getenv("ENV", "dev")
USE_HTTPS = os.getenv("USE_HTTPS", "False") == "True"

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.getenv(
    "DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
if ENV == "dev" and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

if ENV != "dev" and USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

CSRF_TRUSTED_ORIGINS = [
    x.strip()
    for x in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if x.strip()
]

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "fr")
TIME_ZONE = os.getenv("TIME_ZONE", "Africa/Brazzaville")
USE_I18N = True
USE_TZ = True

# Auth front
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "Kerene's Digital <no-reply@kerenes-digital.com>")

SITE_URL = os.getenv("SITE_URL", "https://kerenes-digital.com")
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


WAGTAILDOCS_DOCUMENT_MODEL = "documents.CustomDocument"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "django.contrib.humanize",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # Project apps
    "core",
    "pages",
    "blog",
    "contact",
    "footer",
    "widget_tweaks",
    "documents",
    "library",
    "diagnostic",
    "formation",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.main_menu",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_DIRS = []  # ou crée BASE_DIR/static


# Whitenoise
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

WAGTAIL_SITE_NAME = "Kerene's Digital"
WAGTAILADMIN_BASE_URL = os.getenv(
    "WAGTAILADMIN_BASE_URL", "http://localhost:8000")
