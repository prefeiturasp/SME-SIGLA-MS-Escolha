"""Configurações Django do projeto ms-escolha."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DJANGO_ENVIRONMENT = os.environ.get("DJANGO_ENVIRONMENT", "local")
AMBIENTE_APLICACAO = os.environ.get("AMBIENTE_APLICACAO", DJANGO_ENVIRONMENT)
MS_PATH = os.environ.get("MS_PATH", "/ms-escolha")

BASE_DIR = Path(__file__).resolve().parent.parent

# Adiciona a pasta 'apps' ao sys.path do Python
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-your-secret-key-here"
)
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "qa-api-sigla.sme.prefeitura.sp.gov.br",
    "hom-api-sigla.sme.prefeitura.sp.gov.br",
]
CSRF_TRUSTED_ORIGINS = [
    "https://qa-api-sigla.sme.prefeitura.sp.gov.br",
    "https://hom-api-sigla.sme.prefeitura.sp.gov.br",
]

# Application definition
INSTALLED_APPS = [
    "elasticapm.contrib.django",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "auditlog",
    "drf_spectacular",
    "core",
    "escola",
    "parametrizacao",
    "vagas_escolas",
    "escolhas",
]

MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "sigla_sdk.middlewares.CorrelationIdMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sigla_sdk.middlewares.AuditlogJWTMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database
DB_ENGINE = os.environ.get("DB_ENGINE", "django.db.backends.postgresql")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.environ.get("DB_NAME", BASE_DIR / "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": os.environ.get("DB_NAME", "db_sigla"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

_ms_path_segment = (MS_PATH or "/ms-escolha").strip("/")
if DJANGO_ENVIRONMENT != "local":
    STATIC_URL = f"/{_ms_path_segment}/django_static/"
    MEDIA_URL = f"/{_ms_path_segment}/media/"
else:
    STATIC_URL = "/django_static/"
    MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# DRF settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # "sigla_sdk.autenticacao.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.AllowAny",  # Para facilitar testes
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# AuditLog settings
AUDITLOG_INCLUDE_ALL_MODELS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "sigla_sdk.logging.json_formatter.CustomJsonFormatter",
            "format": "%(levelname)s %(asctime)s %(module)s %(filename)s %(lineno)d %(funcName)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "elasticapm": {
            "level": "DEBUG",
            "class": "elasticapm.contrib.django.handlers.LoggingHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "elasticapm"],
            "level": "INFO",
            "propagate": False,
        },
        "escolhas": {
            "handlers": ["console", "elasticapm"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "elasticapm"],
            "level": "ERROR",
            "propagate": False,
        },
        "elasticapm.errors": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "elasticapm.logging": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

ELASTIC_APM = {
    "SERVICE_NAME": os.environ.get(
        "ELASTIC_APM_SERVICE_NAME", "sme-sigla-ms-escolhas"
    ),
    "SECRET_TOKEN": os.environ.get("ELASTIC_APM_SECRET_TOKEN", ""),
    "SERVER_URL": os.environ.get(
        "ELASTIC_APM_SERVER_URL", "http://localhost:8200"
    ),
    "SERVER_TIMEOUT": os.environ.get("ELASTIC_APM_SERVER_TIMEOUT", "35s"),
    "ENVIRONMENT": os.environ.get(
        "ELASTIC_APM_ENVIRONMENT", AMBIENTE_APLICACAO
    ),
    "ENABLED": os.environ.get("ELASTIC_APM_ENABLED", "0") == "1",
    "CAPTURE_BODY": os.environ.get("ELASTIC_APM_CAPTURE_BODY", "all"),
    "CAPTURE_HEADERS": os.environ.get("ELASTIC_APM_CAPTURE_HEADERS", "1")
    == "1",
    "TRANSACTION_SAMPLE_RATE": float(
        os.environ.get("ELASTIC_APM_TRANSACTION_SAMPLE_RATE", "0.3")
    ),
    "METRICS_INTERVAL": os.environ.get("ELASTIC_APM_METRICS_INTERVAL", "10s"),
    "FLUSH_INTERVAL": os.environ.get("ELASTIC_APM_FLUSH_INTERVAL", "10s"),
    "MAX_BATCH_EVENT_COUNT": int(
        os.environ.get("ELASTIC_APM_MAX_BATCH_EVENT_COUNT", "1000")
    ),
    "MAX_QUEUE_EVENT_COUNT": int(
        os.environ.get("ELASTIC_APM_MAX_QUEUE_EVENT_COUNT", "1000")
    ),
    "TRANSACTION_MAX_SPANS": int(
        os.environ.get("ELASTIC_APM_TRANSACTION_MAX_SPANS", "500")
    ),
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "LOG_LEVEL": os.environ.get("ELASTIC_APM_LOG_LEVEL", "INFO"),
    "LOG_ECS_REFORMATTING": os.environ.get(
        "ELASTIC_APM_LOG_ECS_REFORMATTING", "off"
    ),
    'RECORDING': True,
    'TRANSACTIONS_ROOT_UNNAMED': True,
    'CAPTURE_BODY': 'all',
    'CAPTURE_HEADERS': True,
    'CAPTURE_ERRORS': True,
    'CAPTURE_PERFORMANCE': True,
    'CAPTURE_TRANSACTIONS': True,
    'CAPTURE_SPANS': True,
    'CAPTURE_TRANSACTION_STACKTRACES': True,
    'CAPTURE_TRANSACTION_STACKTRACES_LIMIT': 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Escolha Sigla API",
    "DESCRIPTION": "API para o sistema de escolha de sigla",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # "APPEND_COMPONENTS": {
    #     "securitySchemes": {
    #         "ApiKeyAuth": {
    #             "type": "apiKey",
    #             "in": "header",
    #             "name": "X-API-Key",
    #         }
    #     }
    # },
    # "SECURITY": [{"ApiKeyAuth": []}],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}

SMEINTEGRACAO_API_URL = os.environ.get("SMEINTEGRACAO_API_URL")
SMEINTEGRACAO_API_TOKEN = os.environ.get("SMEINTEGRACAO_API_TOKEN")

# MS URLs e API Keys
API_KEY = os.environ.get("API_KEY", "api-key-escolhas")
API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "X-API-Key")

# External Services
CANDIDATOS_API_URL = os.environ.get(
    "CANDIDATOS_API_URL", "http://localhost:8002"
)
CANDIDATOS_API_KEY = os.environ.get("CANDIDATOS_API_KEY", "api-key-candidatos")
CANDIDATOS_API_TIMEOUT = int(os.environ.get("CANDIDATOS_API_TIMEOUT", 30))

PROCESSOS_CONVOCACAO_API_URL = os.environ.get(
    "PROCESSOS_CONVOCACAO_API_URL", "http://localhost:8000"
)
PROCESSOS_CONVOCACAO_API_KEY = os.environ.get(
    "PROCESSOS_CONVOCACAO_API_KEY", "api-key-processos-convocacao"
)
PROCESSOS_CONVOCACAO_API_TIMEOUT = int(
    os.environ.get("PROCESSOS_CONVOCACAO_API_TIMEOUT", 30)
)

CONCURSOS_API_URL = os.environ.get(
    "CONCURSOS_API_URL", "http://localhost:8001"
)
CONCURSOS_API_KEY = os.environ.get(
    "CONCURSOS_API_KEY", "api-key-processos-concursos"
)

from datetime import timedelta

JWT_SIGNING_KEY = os.environ.get(
    "JWT_SIGNING_KEY", os.environ.get("SECRET_KEY", "fallback-só-dev")
)

SIMPLE_JWT = {
    "SIGNING_KEY": JWT_SIGNING_KEY,
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=1440),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
