"""
Django production settings.
DEBUG=False, strict CORS, secure defaults.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# CORS — only allow the frontend origin in production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://frontend:3000',
]

# Security hardening
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = False      # Set True behind HTTPS
SESSION_COOKIE_SECURE = False   # Set True behind HTTPS
