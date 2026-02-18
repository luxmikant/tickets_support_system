"""
Django development settings.
DEBUG=True, relaxed CORS, browsable API enabled.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['*']

# Allow all CORS origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Enable browsable API in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Use SQLite as fallback for local dev without Docker
import os
if not os.environ.get('POSTGRES_DB'):
    DATABASES = {  # noqa: F811
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }
