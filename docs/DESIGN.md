# Support Ticket System — Design & Requirements Document

## 1. System Overview

A containerized support ticket system where users submit tickets, an LLM auto-classifies them by category and priority, and users can review/override suggestions. Includes a stats dashboard with real-time aggregated metrics.

**Tech Stack:**
- **Backend:** Django 5.x + Django REST Framework + PostgreSQL 16
- **Frontend:** React 18 (CRA) + Tailwind CSS
- **LLM:** Google Gemini 1.5 Flash
- **Infrastructure:** Docker + Docker Compose + Nginx + Gunicorn

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌──────────┐    ┌────────────────────┐    ┌─────────────┐  │
│  │ Frontend │    │      Backend       │    │  PostgreSQL  │  │
│  │  (nginx) │───▶│   (gunicorn +      │───▶│   (pg 16)   │  │
│  │  :3000   │    │    django)         │    │   :5432      │  │
│  │          │    │    :8000           │    │              │  │
│  └──────────┘    │                    │    └─────────────┘  │
│                  │    ┌────────────┐  │                      │
│                  │    │ LLM Service│──┼──▶ Google Gemini API │
│                  │    └────────────┘  │       (external)     │
│                  └────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

**Request Flow:**
1. Browser → Nginx (port 3000) → serves React static files
2. API calls: Nginx proxies `/api/*` → Gunicorn (port 8000) → Django/DRF
3. Django → PostgreSQL for data operations
4. Django → Google Gemini API for classification (async-capable)

---

## 3. Data Model

### 3.1 Ticket Entity

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | AutoField (PK) | Auto-increment | Default Django PK |
| `title` | CharField(200) | NOT NULL, max_length=200 | Required |
| `description` | TextField | NOT NULL | Full problem description |
| `category` | CharField(20) | NOT NULL, CHECK constraint | Choices: billing, technical, account, general |
| `priority` | CharField(20) | NOT NULL, CHECK constraint | Choices: low, medium, high, critical |
| `status` | CharField(20) | NOT NULL, CHECK constraint, default='open' | Choices: open, in_progress, resolved, closed |
| `created_at` | DateTimeField | auto_now_add=True, indexed | Sort key for newest-first |

### 3.2 Database Constraints (enforced at DB level)

```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(category__in=['billing', 'technical', 'account', 'general']),
            name='valid_category'
        ),
        models.CheckConstraint(
            check=models.Q(priority__in=['low', 'medium', 'high', 'critical']),
            name='valid_priority'
        ),
        models.CheckConstraint(
            check=models.Q(status__in=['open', 'in_progress', 'resolved', 'closed']),
            name='valid_status'
        ),
    ]
    indexes = [
        models.Index(fields=['-created_at'], name='idx_ticket_created'),
        models.Index(fields=['category'], name='idx_ticket_category'),
        models.Index(fields=['priority'], name='idx_ticket_priority'),
        models.Index(fields=['status'], name='idx_ticket_status'),
    ]
```

---

## 4. API Design

### 4.1 Endpoints

| Method | Endpoint | Description | Response Code |
|--------|----------|-------------|---------------|
| POST | `/api/tickets/` | Create a new ticket | 201 Created |
| GET | `/api/tickets/` | List tickets (filtered, newest first) | 200 OK |
| PATCH | `/api/tickets/<id>/` | Update ticket fields | 200 OK |
| GET | `/api/tickets/stats/` | Aggregated statistics | 200 OK |
| POST | `/api/tickets/classify/` | LLM classification | 200 OK |

### 4.2 Query Parameters (GET /api/tickets/)

| Param | Type | Example | Behavior |
|-------|------|---------|----------|
| `category` | string | `?category=billing` | Exact match filter |
| `priority` | string | `?priority=high` | Exact match filter |
| `status` | string | `?status=open` | Exact match filter |
| `search` | string | `?search=login issue` | Searches title + description (case-insensitive) |

All filters are combinable: `?category=technical&priority=high&search=error`

### 4.3 Stats Response Schema

```json
{
    "total_tickets": 124,
    "open_tickets": 67,
    "avg_tickets_per_day": 8.3,
    "priority_breakdown": {
        "low": 30, "medium": 52, "high": 31, "critical": 11
    },
    "category_breakdown": {
        "billing": 28, "technical": 55, "account": 22, "general": 19
    }
}
```

**Implementation rule:** Must use `aggregate()` / `annotate()` — no Python-level loops.

### 4.4 Classify Request/Response

**Request:**
```json
{ "description": "I can't log into my account after changing my password" }
```

**Response (success):**
```json
{ "suggested_category": "account", "suggested_priority": "high" }
```

**Response (LLM failure — graceful fallback):**
```json
{
    "suggested_category": "general",
    "suggested_priority": "medium",
    "warning": "LLM service unavailable, using defaults"
}
```

### 4.5 Error Response Envelope (all errors)

```json
{
    "error": "Validation Error",
    "details": {
        "title": ["This field is required."]
    }
}
```

---

## 5. Middleware Stack

**Execution order (top → bottom on request, bottom → top on response):**

| # | Middleware | Purpose |
|---|-----------|---------|
| 1 | `CorsMiddleware` | Handle CORS preflight early |
| 2 | `SecurityMiddleware` | HSTS, SSL redirect |
| 3 | `RequestLoggingMiddleware` ★ | Log method, path, status, duration |
| 4 | `ExceptionHandlingMiddleware` ★ | Catch unhandled exceptions → JSON 500 |
| 5 | `SessionMiddleware` | Session handling |
| 6 | `CommonMiddleware` | URL normalization |
| 7 | `CsrfViewMiddleware` | CSRF protection |
| 8 | `AuthenticationMiddleware` | Request.user |
| 9 | `MessageMiddleware` | Flash messages |

★ = Custom middleware we implement

### 5.1 RequestLoggingMiddleware

```
INFO  | POST /api/tickets/ → 201 (45ms)
WARN  | GET /api/tickets/999/ → 404 (12ms)
ERROR | POST /api/tickets/ → 500 (230ms)
```

### 5.2 ExceptionHandlingMiddleware

- Catches exceptions not handled by DRF (middleware-level errors)
- Returns `{"error": "Internal server error", "detail": "..."}` with status 500
- Logs full traceback to server logs
- Never exposes raw tracebacks in production (`DEBUG=False`)

---

## 6. LLM Integration Design

### 6.1 Choice: Google Gemini 1.5 Flash

**Rationale:**
- Free tier with generous rate limits (good for assessment/demo)
- Fast response times (~0.5-1.5s) — important for UX during typing
- Strong at structured JSON output without extra coercion
- Official Python SDK (`google-generativeai`)

### 6.2 Service Architecture

```
ClassifyView (DRF)
    └── LLMService.classify(description)
            ├── Build prompt with description
            ├── Call Gemini API (10s timeout)
            ├── Parse JSON response
            ├── Validate against allowed choices
            └── Return result or graceful fallback
```

**Separation of concerns:** The LLM logic lives entirely in `tickets/services/llm_service.py`, making it:
- Testable (mock the API call in tests)
- Swappable (switch to OpenAI/Anthropic by changing one file)
- Reusable (can be called from views, management commands, Celery tasks)

### 6.3 Prompt Design

The prompt is a constant stored in the service module. Key design principles:
- Explicit output format (JSON only, no extra text)
- Clear category/priority definitions with examples
- Constrained output space (only valid choices)

### 6.4 Failure Modes & Handling

| Failure | Handling |
|---------|----------|
| API key missing/invalid | Return defaults + warning |
| API timeout (>10s) | Return defaults + warning |
| API rate limited | Return defaults + warning |
| Response not valid JSON | Return defaults + warning |
| Response has invalid choice values | Return defaults + warning |
| Network unreachable | Return defaults + warning |

**Critical rule:** Ticket submission must NEVER fail because of LLM issues.

---

## 7. Graceful Shutdown Design

### 7.1 Signal Chain

```
docker-compose down
    └── SIGTERM → entrypoint.sh (trap)
            └── Forward SIGTERM → Gunicorn master
                    └── SIGTERM → Gunicorn workers
                            └── Finish in-flight requests (30s grace)
                                    └── Close DB connections
                                            └── Exit 0
```

### 7.2 Gunicorn Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `workers` | `CPU * 2 + 1` | Optimal worker count |
| `worker_class` | `gthread` | Thread-based for I/O (LLM calls) |
| `threads` | `4` | Threads per worker |
| `graceful_timeout` | `30` | Seconds for workers to finish on SIGTERM |
| `timeout` | `120` | Max request duration |
| `max_requests` | `1000` | Periodic restart to prevent memory leaks |
| `max_requests_jitter` | `50` | Randomize restart to avoid thundering herd |
| `preload_app` | `True` | Load Django before fork (shared memory) |

### 7.3 Docker Compose Pairing

```yaml
backend:
  stop_grace_period: 30s  # Matches gunicorn graceful_timeout
```

---

## 8. Frontend Component Tree

```
App.jsx
├── TicketForm.jsx              # Create ticket + LLM pre-fill
│   └── LoadingSpinner.jsx      # During LLM classify call
├── FilterBar.jsx               # Dropdowns + search input
├── TicketList.jsx              # Scrollable ticket list
│   └── TicketCard.jsx          # Individual ticket display
│       └── TicketStatusModal   # Status change popover
└── StatsDashboard.jsx          # Metrics cards + breakdowns
```

**State flow:**
- `App.jsx` holds `refreshKey` counter
- `TicketForm` increments `refreshKey` on successful submit
- `TicketList` and `StatsDashboard` re-fetch when `refreshKey` changes
- `FilterBar` updates filter state in `App.jsx`, which passes to `TicketList`

---

## 9. Environment Variables

| Variable | Service | Required | Example |
|----------|---------|----------|---------|
| `GEMINI_API_KEY` | backend | Yes (for LLM) | `AIza...` |
| `DJANGO_SECRET_KEY` | backend | Yes | `django-insecure-...` |
| `DJANGO_SETTINGS_MODULE` | backend | Yes | `config.settings.production` |
| `POSTGRES_DB` | db, backend | Yes | `tickets_db` |
| `POSTGRES_USER` | db, backend | Yes | `tickets_user` |
| `POSTGRES_PASSWORD` | db, backend | Yes | `secure_password` |
| `DATABASE_URL` | backend | Auto-built | `postgres://...` |

---

## 10. Evaluation Alignment

| Criteria (Weight) | How We Address It |
|--------------------|-------------------|
| Does it work? (20%) | Full Docker Compose setup, auto-migrations, healthchecks |
| LLM integration (20%) | Gemini Flash, quality prompt, graceful fallback, pre-fill UX |
| Data modeling (10%) | DB-level CheckConstraints, proper field types, indexes |
| API design (10%) | RESTful ViewSet, correct status codes, composable filters |
| Query logic (10%) | `aggregate()` + `annotate()` in stats — zero Python loops |
| React structure (10%) | Component decomposition, custom hooks, lifted state |
| Code quality (10%) | Service layer pattern, split settings, no dead code |
| Commit history (5%) | Incremental commits per phase |
| README (5%) | Setup, LLM rationale, architecture decisions |
