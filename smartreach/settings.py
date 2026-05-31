"""
SmartReach — Django Ayar Dosyası
Tüm hassas değerler .env dosyasından okunur, asla buraya yazılmaz.
"""

from pathlib import Path
import environ

# BASE_DIR: projenin kök klasörü (manage.py'nin bulunduğu yer)
BASE_DIR = Path(__file__).resolve().parent.parent

# environ kütüphanesi .env dosyasını otomatik okur
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

# ── Güvenlik ──────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ── Uygulamalar ───────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",          # allauth zorunlu kılar

    # Üçüncü taraf
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "rest_framework",
    "crispy_forms",
    "crispy_tailwind",
    "django_celery_beat",

    # Proje uygulamaları
    "accounts",
    "leads",
    "campaigns",
    "emails",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # allauth zorunlu
]

ROOT_URLCONF = "smartreach.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # templates/ klasörünü global olarak tanıt
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "smartreach.wsgi.application"

# ── Veritabanı (PostgreSQL) ───────────────────────────────────
# DATABASE_URL formatı: postgres://kullanici:sifre@host:port/dbadi
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# ── Şifre Doğrulama ───────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Dil ve Zaman ──────────────────────────────────────────────
LANGUAGE_CODE = "tr-tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# ── Statik Dosyalar ───────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Medya Dosyaları (CSV upload vs.) ─────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Django Allauth Ayarları ───────────────────────────────────
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.backends.AuthenticationBackend",
]
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}     # allauth 65+ yeni sözdizimi
ACCOUNT_EMAIL_VERIFICATION = "none"  # Geliştirme aşamasında kapalı
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Google OAuth2 sağlayıcı ayarları
# APP buraya yazılmıyor — client_id/secret admin DB'den (setup_oauth komutuyla) alınıyor
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.readonly",
        ],
        "AUTH_PARAMS": {"access_type": "offline"},  # refresh_token almak için
    }
}

# gmail_service.py için ayrıca erişilebilir
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")

# ── Celery (Görev Kuyruğu) ────────────────────────────────────
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True

# ── Google Gemini API ─────────────────────────────────────────
GEMINI_API_KEY = env("GEMINI_API_KEY")

# ── Tracking Pixel ────────────────────────────────────────────
APP_BASE_URL = env("APP_BASE_URL", default="http://localhost:8000")

# ── Crispy Forms (Tailwind CSS) ───────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
