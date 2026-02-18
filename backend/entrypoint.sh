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

# --- Wait for PostgreSQL to be ready ---
echo "[1/4] Waiting for database..."
while ! python -c "
import os, psycopg2
conn = psycopg2.connect(
    dbname=os.environ.get('POSTGRES_DB', 'tickets_db'),
    user=os.environ.get('POSTGRES_USER', 'tickets_user'),
    password=os.environ.get('POSTGRES_PASSWORD', 'tickets_password'),
    host=os.environ.get('POSTGRES_HOST', 'db'),
    port=os.environ.get('POSTGRES_PORT', '5432'),
)
conn.close()
" 2>/dev/null; do
    echo "  Database not ready — retrying in 2s..."
    sleep 2
done
echo "  Database is ready!"

# --- Apply migrations ---
echo "[2/4] Applying database migrations..."
python manage.py migrate --noinput
echo "  Migrations applied!"

# --- Collect static files ---
echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true
echo "  Static files collected!"

# --- Start Gunicorn ---
echo "[4/4] Starting Gunicorn..."
echo "  Workers: ${GUNICORN_WORKERS:-auto}"
echo "  Bind: 0.0.0.0:8000"
echo "  Graceful timeout: 30s"
echo "========================================"

# Use exec to replace the shell process with Gunicorn.
# This ensures SIGTERM from Docker goes directly to Gunicorn
# (not trapped by the shell), enabling graceful shutdown.
exec gunicorn config.wsgi:application --config gunicorn.conf.py
