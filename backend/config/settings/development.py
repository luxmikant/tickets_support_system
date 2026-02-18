"""
Django development settings.
DEBUG=True, relaxed CORS, browsable API enabled.

How to run locally (without Docker):
    1. pip install -r requirements.txt
    2. export DJANGO_SETTINGS_MODULE=config.settings.development
    3. python manage.py migrate
    4. python manage.py runserver

    The POSTGRES_DB check below auto-falls back to SQLite when no
    database env vars are set, so no Postgres installation is required
    for quick local development.

How to run with Docker (full stack):
    1. cp .env.example .env   (and fill in values)
    2. docker-compose up --build
    Uses docker-compose.yml with DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Enable the DRF browsable API UI in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# ---------------------------------------------------------------------------
# SQLite fallback for local dev without any running database
#
# Triggered when POSTGRES_DB is NOT set in the environment.
# This lets developers run `python manage.py runserver` immediately
# without installing or configuring PostgreSQL locally.
#
# To force PostgreSQL locally (e.g. to test Supabase SSL):
#   export POSTGRES_DB=your_db  (plus other POSTGRES_* vars)
# ---------------------------------------------------------------------------
if not os.environ.get('POSTGRES_DB'):
    DATABASES = {  # noqa: F811
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }
