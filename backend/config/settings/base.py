"""
Django base settings for Support Ticket System.
Common settings shared across all environments.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# CORE SETTINGS
# =============================================================================

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-in-production'
)

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# INSTALLED APPS
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'django_filters',
    'corsheaders',

    # Local
    'tickets',
]


# =============================================================================
# MIDDLEWARE — order matters
# =============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',                 # 1. CORS first
    'django.middleware.security.SecurityMiddleware',         # 2. Security
    'tickets.middleware.RequestLoggingMiddleware',           # 3. Request logging
    'tickets.middleware.ExceptionHandlingMiddleware',        # 4. Error handling
    'django.contrib.sessions.middleware.SessionMiddleware',  # 5. Sessions
    'django.middleware.common.CommonMiddleware',             # 6. URL normalization
    'django.middleware.csrf.CsrfViewMiddleware',            # 7. CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 8. Auth
    'django.contrib.messages.middleware.MessageMiddleware',  # 9. Messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 10. Clickjacking
]


# =============================================================================
# DATABASE — PostgreSQL via environment variables
# =============================================================================

# ---------------------------------------------------------------------------
# Database configuration
#
# Reads individual POSTGRES_* env vars.
# POSTGRES_SSL_MODE=require  →  used for hosted databases like Supabase
#                               (Supabase enforces SSL on all connections)
# ---------------------------------------------------------------------------
_ssl_mode = os.environ.get('POSTGRES_SSL_MODE', '').strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'tickets_db'),
        'USER': os.environ.get('POSTGRES_USER', 'tickets_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'tickets_password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 60,  # Persistent connections for 60s
        'OPTIONS': {
            'connect_timeout': 10,
            # Add sslmode only when explicitly set (e.g. 'require' for Supabase)
            **({'sslmode': _ssl_mode} if _ssl_mode else {}),
        },
    }
}


# =============================================================================
# DJANGO REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'tickets.exceptions.custom_exception_handler',
}


# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'tickets': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


# =============================================================================
# LLM CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
