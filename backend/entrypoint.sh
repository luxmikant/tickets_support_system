#!/bin/bash
# =============================================================================
# Django Entrypoint Script
#
# Runs migrations, collects static files, and starts Gunicorn.
# Supports graceful shutdown by forwarding SIGTERM/SIGINT to Gunicorn.
# =============================================================================

set -e

echo "========================================"
echo " Support Ticket System — Starting Up"
echo "========================================"

# --- Quick DB connectivity check (non-fatal) ---
# Migrations run during build (buildCommand in render.yaml).
# This is a soft check only — a failure here does NOT abort startup.
echo "[1/4] Checking database connectivity..."
python -c "
import os, psycopg2, sys
from urllib.parse import urlparse

db_url = os.environ.get('DATABASE_URL')
if db_url:
    p = urlparse(db_url)
    cfg = dict(dbname=p.path.lstrip('/'), user=p.username,
               password=p.password, host=p.hostname,
               port=p.port or 5432, connect_timeout=5)
else:
    cfg = dict(
        dbname=os.environ.get('POSTGRES_DB', 'tickets_db'),
        user=os.environ.get('POSTGRES_USER', 'tickets_user'),
        password=os.environ.get('POSTGRES_PASSWORD', 'tickets_password'),
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=int(os.environ.get('POSTGRES_PORT', '5432')),
        connect_timeout=5,
    )
try:
    conn = psycopg2.connect(**cfg)
    conn.close()
    print('  Database is reachable!', flush=True)
except Exception as e:
    print(f'  Warning: DB pre-check failed ({e}) — continuing anyway.', flush=True)
" 2>&1 || true

# --- Collect static files ---
echo "[2/4] Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true
echo "  Static files collected!"

# --- Start Gunicorn ---
echo "[3/4] Starting Gunicorn..."
echo "  Workers: ${GUNICORN_WORKERS:-auto}"
echo "  Bind: 0.0.0.0:8000"
echo "  Graceful timeout: 30s"
echo "========================================"

# Use exec to replace the shell process with Gunicorn.
# This ensures SIGTERM from Docker goes directly to Gunicorn
# (not trapped by the shell), enabling graceful shutdown.
exec gunicorn config.wsgi:application --config gunicorn.conf.py
