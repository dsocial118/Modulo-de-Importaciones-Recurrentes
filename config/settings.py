"""Configuración del prototipo de RUNAC.

**Esto es un prototipo.** No es el módulo de SISOC y no está preparado para
producción: no tiene auditoría de accesos, ni control de alcance territorial, ni
las validaciones de seguridad que exige el repositorio.

Sirve para que el equipo técnico de RUNAC pruebe el circuito con datos de prueba
y decida cómo tiene que funcionar. Recién después se integra a SISOC como módulo.

Las versiones son las mismas que usa SISOC (`requirements/base.txt`), para que lo
que se escriba acá se pueda mudar sin sorpresas.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# El prototipo no maneja datos reales, así que la clave no es un secreto.
# Al integrarlo a SISOC, esto se descarta.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "prototipo-runac-no-usar-en-produccion")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

# Se expone por un túnel, así que se aceptan hosts externos.
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
    "http://localhost:8100",
    "http://127.0.0.1:8100",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "runac",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "runac.context.datos_de_sesion",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# La misma base donde viven las tres capas. El prototipo no crea el modelo:
# lo lee. La estructura la produce la skill runac-capa1.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DATABASE_NAME", "runac"),
        "USER": os.getenv("DATABASE_USER", "root"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "runac_local"),
        "HOST": os.getenv("DATABASE_HOST", "mysql"),
        "PORT": os.getenv("DATABASE_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

AUTH_PASSWORD_VALIDATORS = []  # prototipo: no molestar al equipo con esto

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/entrar/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/entrar/"

# Carpetas de trabajo, montadas desde el compose.
RUNAC_CAPA1 = Path(os.getenv("RUNAC_CAPA1", "/trabajo/capa1"))
RUNAC_PLANTILLAS = RUNAC_CAPA1 / "plantillas"
RUNAC_CARGAS = BASE_DIR / "media" / "cargas"

# Marca visible en todas las pantallas. No se saca hasta que deje de ser prototipo.
RUNAC_ES_PROTOTIPO = True
RUNAC_AVISO_PROTOTIPO = "PROTOTIPO · datos de prueba · no es el sistema definitivo"
