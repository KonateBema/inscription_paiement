"""
Django settings for config project.
"""

import os
from pathlib import Path


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

# ------------------------------------------------------------
# DEBUG
# ------------------------------------------------------------
#
# LOCAL :
#     DEBUG=True par défaut
#
# RENDER :
#     Mettre DEBUG=False dans les Environment Variables
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
# Render fournit automatiquement le nom d'hôte externe
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
# Exemple dans Render :
#
# ALLOWED_HOSTS=
# gestion-bulletins-gem.onrender.com
# ============================================================

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

    # --------------------------------------------------------
    # Application du projet
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
    # Gestion des fichiers statiques sur Render
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
# SQLite utilisé actuellement.
#
# LOCAL :
#     db.sqlite3
#
# RENDER :
#     db.sqlite3
#
# IMPORTANT :
# Pour le moment, aucune connexion PostgreSQL n'est utilisée.
# ============================================================

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
# Dossier contenant les fichiers statiques de l'application
# ------------------------------------------------------------

STATICFILES_DIRS = [
    BASE_DIR / "gestion" / "static",
]

# ------------------------------------------------------------
# Dossier généré par collectstatic
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
#
# Exemple :
#
# media/
# └── candidats/
#     └── photos/
#
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
# RENDER :
#     Tu peux configurer SMTP avec les variables
#     d'environnement.
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

    # Redirige HTTP vers HTTPS
    SECURE_SSL_REDIRECT = True

    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    # --------------------------------------------------------
    # Security Headers
    # --------------------------------------------------------

    SECURE_CONTENT_TYPE_NOSNIFF = True

    X_FRAME_OPTIONS = "DENY"