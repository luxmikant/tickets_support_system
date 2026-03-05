# Render Deployment Checklist

## Pre-Deployment

- [ ] Fork/clone repository to your GitHub account
- [ ] Create Supabase project and note connection details
- [ ] Generate Google Gemini API key
- [ ] Create Render account and link GitHub

## Configuration Files

- [x] `render.yaml` — Blueprint configuration
- [x] `backend/config/settings/render.py` — Render-optimized Django settings
- [x] `.env.render` — Environment variable template
- [x] `backend/requirements.txt` — Updated with production packages
- [x] `docs/RENDER_DEPLOYMENT.md` — Full deployment guide

## Render Dashboard Setup

### Create Web Service

- [ ] Go to [dashboard.render.com](https://dashboard.render.com)
- [ ] Click **New +** → **Web Service**
- [ ] Connect GitHub repository: `tickets_support_system`
- [ ] Set **Root Directory**: `backend`

### Build & Deploy Settings

- [ ] **Build Command**:
  ```bash
  pip install --upgrade pip && \
  pip install -r requirements.txt && \
  python manage.py collectstatic --noinput && \
  python manage.py makemigrations --noinput && \
  python manage.py migrate --noinput
  ```

- [ ] **Start Command**:
  ```bash
  gunicorn -c gunicorn.conf.py config.wsgi:application
  ```

### Environment Variables (Mark as Secret where noted)

| Variable | Value | Secret |
|----------|-------|--------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.render` | ❌ |
| `DJANGO_SECRET_KEY` | (generate random string) | ✅ |
| `DJANGO_ALLOWED_HOSTS` | `support-ticket-backend.onrender.com` | ❌ |
| `POSTGRES_ENGINE` | `django.db.backends.postgresql` | ❌ |
| `POSTGRES_DB` | `postgres` | ❌ |
| `POSTGRES_USER` | `postgres` | ❌ |
| `POSTGRES_PASSWORD` | (from Supabase) | ✅ |
| `POSTGRES_HOST` | `db.xxxxxxxxxxxx.supabase.co` | ❌ |
| `POSTGRES_PORT` | `5432` | ❌ |
| `GEMINI_API_KEY` | (your API key) | ✅ |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,https://frontend-url.onrender.com` | ❌ |

## Post-Deployment Verification

- [ ] Service deployed successfully (check **Logs** tab)
- [ ] Database migrations completed without errors
- [ ] API health check passes: `curl https://{service-name}.onrender.com/api/tickets/`
- [ ] Django admin works: `https://{service-name}.onrender.com/admin/`
- [ ] Static files load correctly (check browser console for 404s)
- [ ] Gemini API integration works (test classification endpoint)

## Production Hardening

- [ ] Review and update `ALLOWED_HOSTS` with actual domain
- [ ] Verify HTTPS redirect is working
- [ ] Test CORS with frontend domain
- [ ] Enable Supabase connection pooling for scalability
- [ ] Monitor Render metrics for performance
- [ ] Set up error logging/monitoring (optional: Sentry, DataDog)

## Ongoing Maintenance

- [ ] Review Render deployment logs weekly
- [ ] Monitor Supabase database performance
- [ ] Keep dependencies updated:
  ```bash
  pip list --outdated
  ```
- [ ] Test backup/restore procedures
- [ ] Review Django security checklist quarterly

## Common Issues & Solutions

### Issue: Database connection fails

**Solution**:
- Verify Supabase credentials in environment variables
- Check if Supabase project is active
- Try Supabase connection pooling (port 6543)

### Issue: Migrations not running

**Solution**:
- Check Render build logs for errors
- Ensure `POSTGRES_PASSWORD` is correctly escaped
- Verify database user has necessary permissions

### Issue: CORS errors from frontend

**Solution**:
- Update `CORS_ALLOWED_ORIGINS` with correct frontend URL
- Restart the service after updating environment variables

### Issue: Static files returning 404

**Solution**:
- Ensure `whitenoise` is in requirements.txt
- Run `python manage.py collectstatic --noinput` locally to test
- Check Django settings for `STATIC_ROOT` and `STATIC_URL`

## Quick Links

- [Render Dashboard](https://dashboard.render.com)
- [Supabase Dashboard](https://app.supabase.com)
- [Render Deployment Guide](./RENDER_DEPLOYMENT.md)
- [Project Repository](https://github.com/luxmikant/tickets_support_system)

---

**Last Updated**: March 5, 2026  
**Status**: ✅ Ready for deployment
