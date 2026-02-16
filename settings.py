from pathlib import Path
import os

# ========================
# BASE DIR
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================
DEBUG = True  # ⚠️ Set False in production
ALLOWED_HOSTS = ["*"]  # ⚠️ Dev only
SECRET_KEY = "django-insecure-change-this-in-production"

# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    # Django defaults
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",

    # Celery apps
    "django_celery_results",
    "django_celery_beat",

    # Local apps
    "credit.apps.CreditConfig",
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ========================
# URL CONFIG
# ========================
ROOT_URLCONF = "urls"

# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # no HTML pages
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

# ========================
# WSGI / ASGI
# ========================
WSGI_APPLICATION = "wsgi.application"
ASGI_APPLICATION = "asgi.application"

# ========================
# DATABASE
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),       # e.g., credit_approval_db
        "USER": os.getenv("POSTGRES_USER"),     # e.g., credit_approval_user
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),           # e.g., credit-approval-db.internal
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# ========================
# Django REST Framework
# ========================
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}

# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================
# STATIC FILES
# ========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ========================
# DEFAULT PRIMARY KEY FIELD
# ========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========================
# CELERY SETTINGS (Redis backend)
# ========================
CELERY_BROKER_URL = os.getenv("REDIS_URL")       # Redis hostname provided by Render
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")