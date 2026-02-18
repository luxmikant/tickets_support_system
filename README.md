# Support Ticket System

A full-stack support ticket management application with LLM-powered auto-classification. Users can submit support tickets, browse/filter them, and view aggregated metrics. When a ticket is submitted, **Google Gemini** automatically suggests a category and priority level based on the description — the user can review and override these suggestions before submitting.

---

## Tech Stack

| Layer          | Technology                                    |
|----------------|-----------------------------------------------|
| Backend        | Django 5.x + Django REST Framework             |
| Database       | PostgreSQL 16                                  |
| Frontend       | React 19 + Tailwind CSS v4                     |
| LLM            | Google Gemini 1.5 Flash                        |
| Production     | Gunicorn (gthread workers) + Nginx             |
| Infrastructure | Docker + Docker Compose                        |

---

## Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- A **Google Gemini API key** (get one free at https://aistudio.google.com/apikey)

### Run the Application

```bash
# 1. Clone the repository
git clone <repo-url>
cd support-ticket-system

# 2. Set your Gemini API key
#    Option A: export in shell
export GEMINI_API_KEY=your-api-key-here

#    Option B: create a .env file in the project root
echo "GEMINI_API_KEY=your-api-key-here" > .env

# 3. Start everything with a single command
docker-compose up --build
```

### Access the App

| Service   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000       |
| Backend API | http://localhost:8000/api/tickets/ |
| Django Admin | http://localhost:8000/admin/ |

> **Note:** The app is fully functional after `docker-compose up`. The LLM auto-classification feature requires a valid Gemini API key — without one, ticket submission still works, just without auto-suggestions.

---

## LLM Choice: Google Gemini 1.5 Flash

### Why Gemini?

1. **Free tier** — Gemini provides a generous free API tier, making it accessible without upfront cost.
2. **Speed** — The 1.5 Flash model is optimized for low-latency responses, which matters for the real-time classify-as-you-type UX.
3. **JSON reliability** — With a constrained prompt and `temperature=0.1`, Gemini consistently returns well-structured JSON output.
4. **Simple SDK** — The `google-generativeai` Python library requires minimal boilerplate compared to alternatives.

### Prompt Design

The classification prompt (located in `backend/tickets/services/llm_service.py`) uses several techniques:

- **Explicit category definitions** with example keywords for each (billing, technical, account, general)
- **Clear priority escalation criteria** (critical = system down/data loss; low = cosmetic/feature requests)
- **Tie-breaking rules** — when uncertain, pick the more specific category and the higher priority (err on caution)
- **Structured output constraint** — the prompt demands pure JSON `{"category": "...", "priority": "..."}` with no additional text

### Error Handling

The LLM integration is designed to **never block ticket creation**:

- If the API key is missing → returns defaults (`general` / `medium`) with a warning
- If the API call times out (10s limit) → returns defaults with a warning
- If the response is malformed JSON → attempts recovery, falls back to defaults
- If the returned category/priority is invalid → silently corrects to defaults
- Frontend shows a subtle warning when suggestions are defaults, but the form remains fully functional

---

## Design Decisions

### Backend Architecture

- **Split settings pattern** — `config/settings/{base,development,production}.py` keeps environment-specific config isolated. The base module contains shared settings, while production adds security headers, strict CORS, and `DEBUG=False`.

- **Service layer for LLM** — `LLMService` is isolated from Django views for testability. The entire Gemini integration can be swapped by modifying one file. All 7 unit tests use mocked API calls.

- **Database-level constraints** — `CheckConstraint` on the Ticket model ensures `category`, `priority`, and `status` can only hold valid values at the PostgreSQL level, not just at the Django/serializer layer.

- **Custom middleware stack** — Two middleware classes handle cross-cutting concerns:
  - `RequestLoggingMiddleware` — logs every request with method, path, status code, and duration (ms)
  - `ExceptionHandlingMiddleware` — catches unhandled exceptions and returns structured JSON errors (hides tracebacks in production)

- **DB-level aggregation** — The `/api/tickets/stats/` endpoint uses Django ORM `aggregate()` and `annotate()` for all statistical computations. No Python-level loops process ticket data.

### Frontend Architecture

- **Component decomposition** — 6 focused components: `TicketForm`, `TicketList`, `TicketCard`, `FilterBar`, `StatsDashboard`, `LoadingSpinner`.

- **Debounced LLM classification** — The classify endpoint is called 1.5 seconds after the user stops typing in the description field (or on blur), preventing excessive API calls while keeping the UX responsive.

- **Optimistic state updates** — After ticket creation or status change, the ticket list and stats dashboard auto-refresh via a shared `refreshKey` prop rather than requiring page reloads.

- **Search debouncing** — Filter bar search input debounces at 300ms before hitting the API.

### Production Hardening

- **Gunicorn with gthread workers** — Multi-threaded workers handle concurrent requests efficiently. `max_requests=1000` with jitter prevents memory bloat from long-running processes.

- **Graceful shutdown** — `stop_grace_period: 30s` in Docker Compose matches Gunicorn's `graceful_timeout`. The entrypoint uses `exec gunicorn` so SIGTERM reaches Gunicorn directly for clean connection draining.

- **Nginx reverse proxy** — The frontend container serves the React build statically and proxies `/api/` requests to the Django backend, matching production deployment patterns.

- **Health checks** — PostgreSQL has a health check; the backend waits for the DB to be ready before running migrations.

---

## API Endpoints

| Method | Endpoint               | Description                                      |
|--------|------------------------|--------------------------------------------------|
| POST   | `/api/tickets/`        | Create a new ticket (returns 201)                |
| GET    | `/api/tickets/`        | List tickets, newest first. Supports `?category=`, `?priority=`, `?status=`, `?search=` (combinable) |
| GET    | `/api/tickets/<id>/`   | Retrieve a single ticket                         |
| PATCH  | `/api/tickets/<id>/`   | Update ticket (status, category, priority)        |
| GET    | `/api/tickets/stats/`  | Aggregated statistics                            |
| POST   | `/api/tickets/classify/` | LLM classification (returns suggested category + priority) |

---

## Project Structure

```
support-ticket-system/
├── backend/
│   ├── config/                  # Django project config
│   │   ├── settings/
│   │   │   ├── base.py          # Shared settings
│   │   │   ├── development.py   # Dev overrides (DEBUG=True)
│   │   │   └── production.py    # Production security settings
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── tickets/                 # Main app
│   │   ├── services/
│   │   │   └── llm_service.py   # Gemini integration + prompt
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_llm_service.py
│   │   ├── models.py            # Ticket model with DB constraints
│   │   ├── serializers.py       # DRF serializers
│   │   ├── views.py             # ViewSet + StatsView + ClassifyView
│   │   ├── filters.py           # django-filter FilterSet
│   │   ├── middleware.py        # Request logging + exception handling
│   │   ├── exceptions.py        # Custom DRF exception handler
│   │   └── admin.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── gunicorn.conf.py
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── TicketForm.jsx
│   │   │   ├── TicketList.jsx
│   │   │   ├── TicketCard.jsx
│   │   │   ├── FilterBar.jsx
│   │   │   ├── StatsDashboard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── api/
│   │   │   └── ticketApi.js
│   │   ├── utils/
│   │   │   └── constants.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docs/
│   ├── DESIGN.md
│   └── TASKS.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Running Tests

```bash
# Backend unit tests (inside the container)
docker-compose exec backend python manage.py test tickets -v2

# Or locally with SQLite (development settings)
cd backend
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py test tickets -v2
```

---

## Environment Variables

| Variable              | Required | Default                | Description                    |
|-----------------------|----------|------------------------|--------------------------------|
| `GEMINI_API_KEY`      | Yes*     | —                      | Google Gemini API key          |
| `POSTGRES_DB`         | No       | `tickets_db`           | Database name                  |
| `POSTGRES_USER`       | No       | `tickets_user`         | Database user                  |
| `POSTGRES_PASSWORD`   | No       | `tickets_password`     | Database password              |
| `DJANGO_SECRET_KEY`   | No       | (insecure default)     | Django secret key              |
| `DJANGO_ALLOWED_HOSTS`| No       | `localhost,127.0.0.1`  | Comma-separated allowed hosts  |

*The app works without it — LLM classification returns defaults instead.
