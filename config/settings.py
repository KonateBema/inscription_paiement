
"""
Django settings for config project.
"""

import os
from pathlib import Path

import dj_database_url


# ============================================================
# BASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-dev-only-key-change-in-production"
)


# ============================================================
# DEBUG
# ============================================================
#
# LOCAL :
#     DEBUG=True
#
# RENDER :
#     DEBUG=False
#
# Dans Render :
#     DEBUG=False
# ============================================================

DEBUG = os.environ.get(
    "DEBUG",
    "True"
).lower() == "true"


# ============================================================
# ALLOWED HOSTS
# ============================================================

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


# ------------------------------------------------------------
# Render
# ------------------------------------------------------------

RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(
        RENDER_EXTERNAL_HOSTNAME
    )


# ------------------------------------------------------------
# Domaines supplémentaires
#
# Exemple :
#
# ALLOWED_HOSTS=gestion-bulletins-gem.onrender.com,uic.eu.com
# ------------------------------------------------------------

EXTRA_ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    ""
)

if EXTRA_ALLOWED_HOSTS:

    ALLOWED_HOSTS.extend(
        host.strip()
        for host in EXTRA_ALLOWED_HOSTS.split(",")
        if host.strip()
    )


# ============================================================
# CSRF TRUSTED ORIGINS
# ============================================================
#
# Nécessaire pour les formulaires POST en HTTPS sur Render.
#
# Exemple Render :
#
# CSRF_TRUSTED_ORIGINS=https://gestion-bulletins-gem.onrender.com
#
# Plusieurs domaines :
#
# CSRF_TRUSTED_ORIGINS=https://gestion-bulletins-gem.onrender.com,https://www.mondomaine.com
# ============================================================

CSRF_TRUSTED_ORIGINS = []

EXTRA_CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    ""
)

if EXTRA_CSRF_TRUSTED_ORIGINS:

    CSRF_TRUSTED_ORIGINS.extend(
        origin.strip()
        for origin in EXTRA_CSRF_TRUSTED_ORIGINS.split(",")
        if origin.strip()
    )


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [

    # --------------------------------------------------------
    # Django
    # --------------------------------------------------------

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    "gestion",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    # --------------------------------------------------------
    # Sécurité
    # --------------------------------------------------------

    "django.middleware.security.SecurityMiddleware",

    # --------------------------------------------------------
    # WhiteNoise
    # Gestion des fichiers statiques
    # --------------------------------------------------------

    "whitenoise.middleware.WhiteNoiseMiddleware",

    # --------------------------------------------------------
    # Sessions
    # --------------------------------------------------------

    "django.contrib.sessions.middleware.SessionMiddleware",

    # --------------------------------------------------------
    # Requêtes communes
    # --------------------------------------------------------

    "django.middleware.common.CommonMiddleware",

    # --------------------------------------------------------
    # CSRF
    # --------------------------------------------------------

    "django.middleware.csrf.CsrfViewMiddleware",

    # --------------------------------------------------------
    # Authentification
    # --------------------------------------------------------

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # --------------------------------------------------------
    # Messages
    # --------------------------------------------------------

    "django.contrib.messages.middleware.MessageMiddleware",

    # --------------------------------------------------------
    # Clickjacking
    # --------------------------------------------------------

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI
# ============================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [

    {
        "BACKEND": (
            "django.template.backends.django."
            "DjangoTemplates"
        ),

        "DIRS": [
            BASE_DIR / "gestion" / "templates",
        ],

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


# ============================================================
# DATABASE
# ============================================================
#
# LOCAL :
#     SQLite
#     db.sqlite3
#
# PRODUCTION :
#     PostgreSQL
#     DATABASE_URL fourni par Render
#
# Fonctionnement :
#
#     DATABASE_URL absente
#             ↓
#          SQLite
#
#     DATABASE_URL présente
#             ↓
#        PostgreSQL
# ============================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)


if DATABASE_URL:

    # --------------------------------------------------------
    # PRODUCTION
    # PostgreSQL
    # --------------------------------------------------------

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }

else:

    # --------------------------------------------------------
    # DEVELOPPEMENT LOCAL
    # SQLite
    # --------------------------------------------------------

    DATABASES = {

        "default": {

            "ENGINE": "django.db.backends.sqlite3",

            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },

    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Africa/Abidjan"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"


# ------------------------------------------------------------
# Dossier des fichiers statiques
# ------------------------------------------------------------

STATICFILES_DIRS = [
    BASE_DIR / "gestion" / "static",
]


# ------------------------------------------------------------
# Dossier collectstatic
# ------------------------------------------------------------

STATIC_ROOT = BASE_DIR / "staticfiles"


# ------------------------------------------------------------
# WhiteNoise
# ------------------------------------------------------------

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# AUTHENTIFICATION
# ============================================================

LOGIN_URL = "/connexion/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/connexion/"


# ============================================================
# EMAIL
# ============================================================
#
# LOCAL :
#     Les emails sont affichés dans le terminal.
#
# PRODUCTION :
#     Configuration SMTP via variables Render.
# ============================================================

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)


EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    ""
)


EMAIL_PORT = int(
    os.environ.get(
        "EMAIL_PORT",
        "587"
    )
)


EMAIL_USE_TLS = (
    os.environ.get(
        "EMAIL_USE_TLS",
        "True"
    ).lower() == "true"
)


EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    ""
)


EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    ""
)


DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "webmaster@localhost"
)


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# ============================================================
# PRODUCTION / RENDER
# ============================================================

if not DEBUG:

    # --------------------------------------------------------
    # HTTPS
    # --------------------------------------------------------
    #
    # Render utilise un proxy HTTPS devant Django.
    # --------------------------------------------------------

    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )


    # --------------------------------------------------------
    # Redirection HTTP → HTTPS
    # --------------------------------------------------------

    SECURE_SSL_REDIRECT = True


    # --------------------------------------------------------
    # Cookies sécurisés
    # --------------------------------------------------------

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True


    # --------------------------------------------------------
    # Security Headers
    # --------------------------------------------------------

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"


    # --------------------------------------------------------
    # HSTS
    # --------------------------------------------------------
    #
    # À activer uniquement lorsque le domaine HTTPS
    # fonctionne correctement.
    # --------------------------------------------------------

    SECURE_HSTS_SECONDS = 31536000

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

