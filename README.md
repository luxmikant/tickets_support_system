<div align="center">

# 🎫 Support Ticket System

**A full-stack AI-powered support ticket management platform**

[![Django](https://img.shields.io/badge/Django-6.0.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19.2-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

*Submit tickets → AI classifies them instantly → you review and override*

</div>

---

## ✨ Features

- **🤖 AI Auto-Classification** — Google Gemini analyses ticket descriptions in real time and suggests a category + priority. Debounced to avoid spamming the API; triggers 1.5 s after you stop typing
- **✏️ User Override** — Suggestions are pre-filled but fully editable. AI-suggested dropdowns are highlighted in blue so you always know which fields were auto-filled
- **📊 Live Statistics Dashboard** — Ticket counts by status, category, and priority, computed at the database level
- **🔍 Filtering & Search** — Filter by category, priority, status; full-text search, all combinable and debounced
- **🐳 One-Command Deployment** — `docker-compose up --build` starts the database, backend, and frontend with health checks and auto-migration
- **🛡️ Defence-in-Depth** — DB-level constraints, request logging middleware, structured JSON error responses, graceful Gunicorn shutdown

---

## 🏗️ Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **Backend** | Django 6.0.2 + Django REST Framework | Split settings (base / dev / prod) |
| **Database** | PostgreSQL 16 | DB-level `CheckConstraint` on every enum field |
| **Frontend** | React 19 + Tailwind CSS v3 | CRA build served via Nginx |
| **LLM** | Google Gemini 1.5 Flash | Few-shot + chain-of-thought prompt, keyword pre-extraction |
| **WSGI** | Gunicorn (gthread workers) | `max_requests=1000` with jitter to prevent memory bloat |
| **Proxy** | Nginx | Serves React build; proxies `/api/` and `/admin/` to Django |
| **Infra** | Docker + Docker Compose | Healthchecks, `start_period`, retry limits |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed on your machine
- A **Google Gemini API key** — get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1 — Clone & configure

```bash
git clone https://github.com/luxmikant/tickets_support_system.git
cd tickets_support_system

# Create your .env file (copy from the example)
cp .env.example .env
# Then open .env and set GEMINI_API_KEY=your-key-here
```

### 2 — Launch the full stack

```bash
docker-compose up --build
```

Docker Compose will:
1. 🗄️ Start **PostgreSQL** and wait until it passes the health check
2. ⚙️ Start **Django** — runs `makemigrations` + `migrate` + `collectstatic` automatically
3. 🌐 Start **React/Nginx** — serves the production build and proxies API calls

### 3 — Open the app

| Service | URL |
|---|---|
| 🌐 **Frontend** | http://localhost:3000 |
| ⚙️ **Backend API** | http://localhost:8000/api/tickets/ |
| 🔧 **Django Admin** | http://localhost:8000/admin/ |

> **Without a Gemini key** the app is fully functional — ticket creation and management work normally. LLM suggestions are silently skipped and the keyword-based heuristic classifies instead.

---

## 🤖 LLM Integration & Query Optimization

This is the core technical feature of the system. The classification pipeline lives in [`backend/tickets/services/llm_service.py`](backend/tickets/services/llm_service.py) and uses **six query optimization techniques** to maximise accuracy.

### Why Google Gemini 1.5 Flash?

| Criterion | Reason |
|---|---|
| **Free tier** | Generous free API quota — no credit card needed for development |
| **Latency** | Flash variant is optimised for low-latency inference (< 2 s for classification) |
| **JSON output** | Reliably follows structured output instructions with low temperature |
| **SDK simplicity** | `google-generativeai` Python library needs < 10 lines for a full call |

---

### 🔬 Optimization Technique 1 — Few-Shot Prompting

> *Ground the model with concrete examples so it doesn't have to guess the output format.*

Instead of describing what to do in abstract terms, the prompt includes **5 labelled input/output pairs** covering each ticket type and an urgency escalation case:

```
Input:  "I was charged twice for my subscription this month."
Output: {"suggested_category": "billing", "suggested_priority": "medium"}

Input:  "Our entire team cannot access the platform — production is down. Urgent!"
Output: {"suggested_category": "technical", "suggested_priority": "critical"}
```

Few-shot examples dramatically reduce the model's tendency to invent new category names or return prose instead of JSON.

---

### 🧠 Optimization Technique 2 — Chain-of-Thought Reasoning

> *Force the model to reason before it answers — reasoning tokens improve final answer quality.*

Each example in the prompt includes an **Analysis step** before the output:

```
Input:  "The app crashes every time I open the dashboard."
Analysis: App crash, no workaround mentioned → technical. Major broken feature → high.
Output: {"suggested_category": "technical", "suggested_priority": "high"}
```

The model is then asked to perform its own analysis step for the input ticket. This intermediate reasoning anchors the final classification and significantly reduces misclassification on ambiguous descriptions.

---

### 🏷️ Optimization Technique 3 — Keyword Pre-Extraction (Signal Injection)

> *Don't make the LLM discover signals itself — extract them with regex and inject them as structured hints.*

Before the prompt is sent, `_extract_signals(description)` scans the description with compiled regex patterns and prepends a **structured hint block**:

```
### Extracted Signals:
⚠️ URGENCY SIGNALS DETECTED: urgent, someone can die, deadline
📌 TECHNICAL keywords: not starting, application
```

This is the key fix for the original problem (*"someone can die" being classified as `medium`*). The LLM receives both the raw text **and** pre-labelled signals — it no longer needs to "discover" urgency in ambiguous phrasing.

**Urgency patterns detected:**
`urgent` · `emergency` · `ASAP` · `immediately` · `life-threatening` · `someone can die` · `deadline` · `cannot wait` · `blocking` · `production down` · `data loss` · `outage`

**Category patterns detected:**
- `billing` — payment, invoice, refund, charge, subscription, pricing, credit card…
- `technical` — bug, error, crash, not working, not starting, broken, timeout, API…
- `account` — login, password, reset, permission, access, 2FA, locked out…

---

### 🎯 Optimization Technique 4 — Near-Deterministic Temperature

> *Classification is not a creative task — reduce randomness to get consistent results.*

| Setting | Value | Reason |
|---|---|---|
| `temperature` | **0.05** | Near-deterministic; same input → same output each time |
| `top_p` | **0.9** | Focused sampling; ignores long-tail token probabilities |
| `max_output_tokens` | **200** | Enough for brief reasoning + JSON; prevents verbose rambling |

The original `temperature=0.1` was lowered further to `0.05`. At this level the model essentially always picks the highest-probability token — which is exactly what we want for a fixed-label classification task.

---

### 🔍 Optimization Technique 5 — Robust JSON Extraction

> *LLMs with chain-of-thought emit reasoning text before the JSON — handle all output shapes.*

The `_parse_response()` method handles three output shapes:

```python
# Shape 1 — clean JSON (ideal)
'{"suggested_category": "technical", "suggested_priority": "critical"}'

# Shape 2 — markdown code block
'```json\n{"suggested_category": "billing", ...}\n```'

# Shape 3 — reasoning text followed by JSON (chain-of-thought output)
'Analysis: The user mentions "crash"...\nOutput: {"suggested_category": "technical", ...}'
```

A targeted regex `r'\{[^{}]*"suggested_category"[^{}]*\}'` extracts the JSON object from anywhere in the response, so chain-of-thought output is handled automatically.

---

### 🛟 Optimization Technique 6 — Keyword Heuristic Fallback

> *When the API is unavailable, don't return a useless `general/medium` — classify from keywords.*

`_keyword_fallback(description)` runs entirely locally with no API call:

1. **Category** — counts keyword matches per category using the same regex patterns as signal extraction. Highest score wins.
2. **Priority** — counts urgency keyword matches:
   - ≥ 3 urgency matches **or** extreme words (die, death, outage, breach) → `critical`
   - ≥ 1 urgency match → `high`
   - Contains broken/error/crash with no urgency → `high`
   - General/no signals → `low` or `medium`

This fallback is **far more useful** than returning `general/medium` — a description mentioning "login", "password", "urgent" will correctly resolve to `account / high` even without internet.

---

### Classification Pipeline — End to End

```
User types description (≥ 20 chars)
         │
         ▼  (debounced 1.5 s / on blur)
  POST /api/tickets/classify/
         │
         ▼
  ClassifyView → ClassifyRequestSerializer (min_length=10, strip whitespace)
         │
         ▼
  LLMService.classify(description)
         │
         ├─── GEMINI_API_KEY set? ──No──► _keyword_fallback()
         │                                        │
         │                               keyword scores + urgency count
         │                                        │
         ▼                                        ▼
  _extract_signals()                     { category, priority }
         │
    urgency + category keywords
         │
         ▼
  _call_gemini()
    ├─ CLASSIFICATION_PROMPT (role + table + priority rules)
    ├─ 5 few-shot examples with chain-of-thought analysis
    ├─ ### Extracted Signals: (injected hints)
    ├─ ### Ticket Description: (raw text)
    └─ temperature=0.05, top_p=0.9, max_tokens=200
         │
         ▼
  _parse_response()
    ├─ strip markdown fences
    ├─ extract JSON via regex (handles embedded reasoning)
    ├─ validate category ∈ {billing, technical, account, general}
    └─ validate priority ∈ {low, medium, high, critical}
         │
         ▼  (on any failure → _keyword_fallback())
  { suggested_category, suggested_priority }
         │
         ▼
  Frontend pre-fills dropdowns with blue highlight
  "(AI suggested — editable)" — user can change and submit
```

---

### LLM Error Handling

The pipeline is designed to **never block ticket creation**:

| Failure scenario | Behaviour |
|---|---|
| No `GEMINI_API_KEY` | Uses keyword heuristic fallback; no warning shown to user |
| API timeout (10 s limit) | Falls back to keyword heuristic; `warning` field added to response |
| Malformed JSON response | Regex extraction attempted; falls back to defaults if still invalid |
| Invalid category/priority value | Silently corrected to `general` / `medium` |
| API quota exceeded / network error | Falls back to keyword heuristic with logged error |

---

## 🗺️ API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tickets/` | Create a new ticket → `201 Created` |
| `GET` | `/api/tickets/` | List tickets, newest first. Filters: `?category=` `?priority=` `?status=` `?search=` |
| `GET` | `/api/tickets/<id>/` | Retrieve a single ticket |
| `PATCH` | `/api/tickets/<id>/` | Update status / category / priority |
| `GET` | `/api/tickets/stats/` | Live aggregated statistics (DB-level computation) |
| `POST` | `/api/tickets/classify/` | LLM classification — returns `{suggested_category, suggested_priority}` |

### Example — classify a ticket

```bash
curl -X POST http://localhost:8000/api/tickets/classify/ \
  -H "Content-Type: application/json" \
  -d '{"description": "Production is down and users cannot log in. This is urgent!"}'
```

```json
{
  "suggested_category": "technical",
  "suggested_priority": "critical"
}
```

---

## 🏛️ Architecture & Design Decisions

### Backend

| Decision | Rationale |
|---|---|
| **Split settings** (`base` / `dev` / `prod`) | Keeps environment-specific config isolated. Production adds `DEBUG=False`, strict CORS, security headers. |
| **Service layer for LLM** | `LLMService` is decoupled from views — swappable, testable, no Django imports needed. |
| **DB-level `CheckConstraint`** | `category`, `priority`, `status` are enforced at PostgreSQL level, not just ORM. Invalid values are rejected even on direct SQL. |
| **`RequestLoggingMiddleware`** | Every request logged with method, path, HTTP status, duration (ms). |
| **`ExceptionHandlingMiddleware`** | Catches unhandled exceptions and returns structured JSON — hides tracebacks in production. |
| **DB-level aggregation** | `stats/` endpoint uses ORM `aggregate()` + `annotate()` — zero Python loops over ticket data. |

### Frontend

| Decision | Rationale |
|---|---|
| **6 focused components** | `TicketForm`, `TicketList`, `TicketCard`, `FilterBar`, `StatsDashboard`, `LoadingSpinner` — single responsibility each. |
| **Debounced LLM calls (1.5 s)** | Prevents spamming the classify endpoint while typing. Also triggers on blur. |
| **Blue highlight on AI dropdowns** | User always knows which fields were auto-filled vs manually chosen. |
| **`refreshKey` pattern** | Ticket list and stats auto-refresh after create/update without page reload. |
| **Search debounce (300 ms)** | Filter bar input waits 300 ms before hitting the API. |

### Infrastructure

| Decision | Rationale |
|---|---|
| **Healthcheck `start_period: 15 s`** | Postgres needs time to initialise before `pg_isready` starts counting failures. |
| **Retry limit in entrypoint** | `MAX_RETRIES=30` (60 s max). Clear error message and `exit 1` if DB never becomes reachable — no infinite loops. |
| **`exec gunicorn`** in entrypoint | Replaces the shell process so `SIGTERM` from Docker goes directly to Gunicorn for graceful connection draining. |
| **`stop_grace_period: 30 s`** | Matches Gunicorn's `graceful_timeout` so in-flight requests complete before forceful kill. |
| **Nginx serves React build** | No `/static/` proxy to Django — React's compiled CSS/JS is served directly from the Nginx container. |

---

## 📁 Project Structure

```
support-ticket-system/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py              # Shared settings
│   │   │   ├── development.py       # DEBUG=True, SQLite option
│   │   │   └── production.py        # Security headers, strict CORS
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── tickets/
│   │   ├── services/
│   │   │   └── llm_service.py       # ★ Gemini integration + 6 optimizations
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_llm_service.py  # 16 unit tests (mocked API)
│   │   ├── models.py                # Ticket model + DB constraints
│   │   ├── serializers.py           # DRF serializers + validation
│   │   ├── views.py                 # TicketViewSet + StatsView + ClassifyView
│   │   ├── filters.py               # django-filter FilterSet
│   │   ├── middleware.py            # RequestLogging + ExceptionHandling
│   │   └── exceptions.py           # Custom DRF exception handler
│   ├── Dockerfile
│   ├── entrypoint.sh               # DB wait loop + migrate + collectstatic
│   ├── gunicorn.conf.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TicketForm.jsx      # ★ Debounced classify + blue AI hints
│   │   │   ├── TicketList.jsx
│   │   │   ├── TicketCard.jsx
│   │   │   ├── FilterBar.jsx
│   │   │   ├── StatsDashboard.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── api/
│   │   │   └── ticketApi.js        # Axios instance + classifyTicket()
│   │   └── utils/
│   │       └── constants.js
│   ├── tailwind.config.js          # Explicit content paths (v3)
│   ├── postcss.config.js
│   ├── nginx.conf                  # Static serve + /api proxy
│   └── Dockerfile
├── docker-compose.yml              # db + backend + frontend with healthchecks
├── .env.example
└── README.md
```

---

## 🧪 Running Tests

```bash
# Run all backend tests inside the running container
docker-compose exec backend python manage.py test tickets -v2

# Or locally (requires Python 3.12+ and pip install -r requirements.txt)
cd backend
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py test tickets -v2
```

**Test coverage:**

| Test file | What it covers |
|---|---|
| `test_models.py` | Ticket model field validation, DB constraints |
| `test_views.py` | All API endpoints (CRUD, stats, classify), filter combinations |
| `test_llm_service.py` | JSON parsing (3 shapes), keyword fallback (8 cases), signal extraction, classify orchestration |

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Recommended | — | Google Gemini API key. Without it, keyword heuristic is used. |
| `POSTGRES_DB` | No | `tickets_db` | PostgreSQL database name |
| `POSTGRES_USER` | No | `tickets_user` | PostgreSQL user |
| `POSTGRES_PASSWORD` | No | `tickets_password` | PostgreSQL password |
| `POSTGRES_HOST` | No | `db` | DB host (`db` = Docker service name) |
| `DJANGO_SECRET_KEY` | Production | *(insecure default)* | Django secret key — **always override in production** |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1,backend` | Comma-separated allowed hosts |
| `DJANGO_SETTINGS_MODULE` | No | `config.settings.production` | Settings module to load |
| `GUNICORN_WORKERS` | No | `3` | Number of Gunicorn worker processes |

---

<div align="center">

Built as a full-stack assessment project · Django + React + PostgreSQL + Google Gemini + Docker

</div>
