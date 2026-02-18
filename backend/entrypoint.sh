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
MAX_RETRIES=30   # 30 × 2s = 60 seconds max wait
RETRIES=0
until python -c "
import os, psycopg2, sys
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', 'tickets_db'),
        user=os.environ.get('POSTGRES_USER', 'tickets_user'),
        password=os.environ.get('POSTGRES_PASSWORD', 'tickets_password'),
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        connect_timeout=3,
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'  Connection error: {e}', flush=True)
    sys.exit(1)
" 2>&1; do
    RETRIES=$((RETRIES + 1))
    if [ "$RETRIES" -ge "$MAX_RETRIES" ]; then
        echo "ERROR: Database did not become ready after $((MAX_RETRIES * 2))s — check your POSTGRES_* environment variables."
        exit 1
    fi
    echo "  Database not ready — retrying in 2s... ($RETRIES/$MAX_RETRIES)"
    sleep 2
done
echo "  Database is ready!"

# --- Generate & apply migrations ---
echo "[2/4] Generating and applying database migrations..."
python manage.py makemigrations --noinput
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
