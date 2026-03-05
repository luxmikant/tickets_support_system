# Render Deployment Guide — Support Ticket System

## Overview

This guide walks you through deploying the Django backend to **Render** using **Supabase PostgreSQL** for the database.

---

## Prerequisites

1. **GitHub Repository** — Your code must be on GitHub (public or private)
   - Fork or use: `https://github.com/luxmikant/tickets_support_system.git`

2. **Supabase Account** — Free tier available at [supabase.com](https://supabase.com)
   - Create a new project and note the connection details

3. **Render Account** — Free tier available at [render.com](https://render.com)
   - Sign up and connect your GitHub account

4. **Google Gemini API Key** — Get free tier at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## Step 1: Set Up Supabase PostgreSQL Database

### 1.1 Create Supabase Project

1. Go to [app.supabase.com](https://app.supabase.com)
2. Click **New Project**
3. Fill in:
   - **Name**: `support-tickets` (or any name)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your Render region
4. Wait for the project to initialize (~5-10 minutes)

### 1.2 Get Connection Details

1. In Supabase Dashboard, go to **Settings** → **Database**
2. Copy the following:
   - **Host**: `db.xxxxxxxxxxxx.supabase.co`
   - **Database**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (the one you set above)

### 1.3 Enable Connection Pooling (Optional but Recommended)

1. In Supabase, go to **Settings** → **Database** → **Connection Pooling**
2. Set **Pool Mode** to `Transaction`
3. Copy the **Pooling Connection String** for later

---

## Step 2: Configure Django for Render

### 2.1 Update Settings

Your `backend/config/settings/render.py` is already created with Render-optimized settings:

```python
# Key features:
# - HTTPS enforcement
# - Supabase PostgreSQL integration
# - Static file handling with WhiteNoise
# - Logging to stdout (Render requirement)
```

The `render.yaml` already references `DJANGO_SETTINGS_MODULE=config.settings.render`.

### 2.2 Verify Requirements

Ensure `backend/requirements.txt` includes:

```
Django>=5.0,<6.1
psycopg2-binary>=2.9
gunicorn>=21.0
django-cors-headers>=4.0
djangorestframework>=3.14
google-generativeai>=0.5.0
whitenoise>=6.0  # For static file serving
dj-database-url>=1.2  # Optional, for DATABASE_URL parsing
```

If missing, update the file:
```bash
pip install whitenoise dj-database-url
```

---

## Step 3: Deploy to Render

### 3.1 Connect GitHub to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Select **Build and deploy from a Git repository**
4. Click **Connect account** and authorize GitHub
5. Select your repository: `tickets_support_system`

### 3.2 Configure Render Service

**Basic Settings:**
- **Name**: `support-ticket-backend`
- **Environment**: `Python 3`
- **Region**: `Ohio` (or closest to Supabase)
- **Plan**: `Free` (or `Starter` for production)

**Build & Deploy:**
- **Root Directory**: `backend`
- **Build Command**:
  ```bash
  pip install --upgrade pip && \
  pip install -r requirements.txt && \
  python manage.py collectstatic --noinput && \
  python manage.py makemigrations --noinput && \
  python manage.py migrate --noinput
  ```
- **Start Command**:
  ```bash
  gunicorn -c gunicorn.conf.py config.wsgi:application
  ```

### 3.3 Set Environment Variables

In the Render dashboard, go to **Environment**:

| Key | Value | Notes |
|-----|-------|-------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.render` | Use Render-optimized settings |
| `DJANGO_SECRET_KEY` | (random string) | Generate a secure key |
| `DJANGO_ALLOWED_HOSTS` | `support-ticket-backend.onrender.com` | Updated after first deploy |
| `POSTGRES_ENGINE` | `django.db.backends.postgresql` | Fixed value |
| `POSTGRES_DB` | `postgres` | From Supabase |
| `POSTGRES_USER` | `postgres` | From Supabase |
| `POSTGRES_PASSWORD` | (your Supabase password) | From Supabase → **Mark as Secret** |
| `POSTGRES_HOST` | `db.xxxxxxxxxxxx.supabase.co` | From Supabase |
| `POSTGRES_PORT` | `5432` | Fixed value |
| `GEMINI_API_KEY` | (your API key) | From Google → **Mark as Secret** |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,https://your-frontend.onrender.com` | Adjust for your frontend |

**⚠️ Mark as Secret:** Click the **Secret** icon for sensitive values (passwords, API keys).

### 3.4 Deploy

1. Click **Deploy**
2. Render will:
   - Clone your repository
   - Run the build command
   - Create the database schema (migrations)
   - Start Gunicorn

Monitor the build in the **Logs** tab.

---

## Step 4: Verify Deployment

### 4.1 Check Health

Your service should be live at: `https://support-ticket-backend.onrender.com`

Test the API:
```bash
curl https://support-ticket-backend.onrender.com/api/tickets/
```

Expected response:
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### 4.2 Check Django Admin

Visit: `https://support-ticket-backend.onrender.com/admin/`

### 4.3 View Logs

In Render dashboard → **Logs** tab to debug issues.

---

## Step 5: Deploy Frontend (Optional)

If deploying the React frontend to Render as well:

1. Create a second Render service for the frontend
2. Use `frontend/` as the root directory
3. Build command: `npm run build`
4. Start command: `npm start`
5. Set `REACT_APP_API_URL=https://support-ticket-backend.onrender.com`

---

## Troubleshooting

### Database Connection Fails

**Error**: `FATAL: Ident authentication failed for user "postgres"`

**Solution**:
1. Verify `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD` are correct
2. Check Supabase project is active
3. Ensure password doesn't contain special characters that need escaping

### Migrations Don't Run

**Error**: `django.db.utils.OperationalError: FATAL: remaining connection slots reserved for non-replication superuser connections`

**Solution**:
1. Increase Supabase connection limit (Settings → Database)
2. Or use connection pooling: `db.xxxxxxxxxxxx.supabase.co:6543` (pooling port)

### Static Files 404

**Error**: CSS/JS returning 404

**Solution**:
1. Ensure `WhiteNoise` is in `requirements.txt`
2. Run: `python manage.py collectstatic --noinput`

### CORS Errors

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
1. Update `CORS_ALLOWED_ORIGINS` in environment variables
2. Include your frontend URL (e.g., `https://support-ticket-frontend.onrender.com`)

---

## Performance Optimization

### 1. Enable Supabase Connection Pooling

In Supabase settings, use the pooling connection string (`port 6543`) instead of direct connection (`port 5432`).

### 2. Upgrade Render Plan

- **Starter**: 0.5 vCPU, optimized for IO
- **Standard**: 1 vCPU, suitable for production

### 3. Add Redis Caching

Update `requirements.txt`:
```bash
pip install django-redis
```

Update `render.py`:
```python
import os
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'unix:///tmp/redis.sock'),
    }
}
```

### 4. Monitor Performance

- Render Dashboard → **Metrics** tab
- Supabase Dashboard → **Database** → **Performance**

---

## Useful Links

- [Render Documentation](https://render.com/docs)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)
- [Django Production Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)

---

## Support

- **Render Support**: [render.com/support](https://render.com/support)
- **Supabase Support**: [supabase.com/support](https://supabase.com/support)
- **Django Docs**: [docs.djangoproject.com](https://docs.djangoproject.com)
