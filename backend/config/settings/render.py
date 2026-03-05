"""
Django Render production settings.
Optimized for Render deployment with Supabase PostgreSQL.
"""

from .base import *  # noqa: F401, F403
import os

DEBUG = False

# =============================================================================
# SECURITY
# =============================================================================

# Get domain from Render environment
ALLOWED_HOSTS = os.environ.get(
    'RENDER_EXTERNAL_HOSTNAME',
    os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
).split(',')

# HTTPS + Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Behind Render's reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# =============================================================================
# DATABASE — Supabase PostgreSQL
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read_committed'
        }
    }
}

# Alternative: Use DATABASE_URL if provided
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )

# =============================================================================
# CORS — Production Settings
# =============================================================================

CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for efficient static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# =============================================================================
# LOGGING
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# PERFORMANCE & CACHE
# =============================================================================

# Simple in-memory cache for development
# Upgrade to Redis in production if needed
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'tickets-backend-cache',
    }
}

# =============================================================================
# GUNICORN
# =============================================================================

# Number of workers (auto-scale based on CPU in Render)
import multiprocessing
GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2))
