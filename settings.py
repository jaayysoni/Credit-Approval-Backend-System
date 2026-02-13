from pathlib import Path
import secrets  # For generating a secret key

# ========================
# BASE DIR
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent  # Assuming settings.py is in <project>/settings.py

# ========================
# SECURITY
# ========================
DEBUG = True
ALLOWED_HOSTS = ["*"]  # For development only

# Generate a secret key if not set (development only)
SECRET_KEY = "django-insecure-" + secrets.token_urlsafe(50)

# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    # Django defaults
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'credit',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",       # Must come before auth
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",    # Required for admin
    "django.contrib.messages.middleware.MessageMiddleware",       # Required for admin
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ========================
# ROOT URLS
# ========================
ROOT_URLCONF = "urls"  # Assuming urls.py is in project root

# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Optional: create a templates/ folder
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
WSGI_APPLICATION = "wsgi.application"  # Ensure wsgi.py is in project root
ASGI_APPLICATION = "asgi.application"  # Ensure asgi.py is in project root

# ========================
# DATABASE
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "credit_system",
        "USER": "credit_user",
        "PASSWORD": "StrongPassword123",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# ========================
# PASSWORD VALIDATORS
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
# DEFAULT AUTO FIELD
# ========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"