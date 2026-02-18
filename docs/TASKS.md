# Support Ticket System — Task Tracker

## Phase 1: Foundation & Configuration
| # | Task | Status | Priority |
|---|------|--------|----------|
| 1.1 | Create project scaffolding (Django project `config`, app `tickets`) | ⬜ | P0 |
| 1.2 | Split Django settings (base / development / production) | ⬜ | P0 |
| 1.3 | Configure PostgreSQL connection via environment variables | ⬜ | P0 |
| 1.4 | Setup `.gitignore`, `.env.example` | ⬜ | P0 |
| 1.5 | Install & configure DRF, django-filter, django-cors-headers | ⬜ | P0 |

## Phase 2: Data Layer
| # | Task | Status | Priority |
|---|------|--------|----------|
| 2.1 | Create `Ticket` model with all fields and choices | ⬜ | P0 |
| 2.2 | Add DB-level `CheckConstraint` for category, priority, status | ⬜ | P0 |
| 2.3 | Add Meta ordering (`-created_at`), indexes, `db_table` | ⬜ | P0 |
| 2.4 | Register model in Django admin | ⬜ | P1 |
| 2.5 | Generate and apply migrations | ⬜ | P0 |

## Phase 3: Middleware & Error Handling
| # | Task | Status | Priority |
|---|------|--------|----------|
| 3.1 | Implement `RequestLoggingMiddleware` (method, path, status, duration) | ⬜ | P0 |
| 3.2 | Implement `ExceptionHandlingMiddleware` (catch unhandled, JSON response) | ⬜ | P0 |
| 3.3 | Create custom DRF exception handler (consistent error envelope) | ⬜ | P0 |
| 3.4 | Register middleware in correct order in settings | ⬜ | P0 |

## Phase 4: API Layer
| # | Task | Status | Priority |
|---|------|--------|----------|
| 4.1 | Create `TicketSerializer`, `TicketUpdateSerializer`, `ClassifySerializer` | ⬜ | P0 |
| 4.2 | Create `TicketFilter` (category, priority, status, search) | ⬜ | P0 |
| 4.3 | Implement `TicketViewSet` (list, create, partial_update) | ⬜ | P0 |
| 4.4 | Implement `StatsView` — DB-level aggregation only | ⬜ | P0 |
| 4.5 | Implement `ClassifyView` — calls LLM service | ⬜ | P0 |
| 4.6 | Wire up URL routing (router + manual endpoints) | ⬜ | P0 |
| 4.7 | Verify proper HTTP status codes (201 on create, 200 on list/patch) | ⬜ | P0 |

## Phase 5: LLM Integration (Google Gemini)
| # | Task | Status | Priority |
|---|------|--------|----------|
| 5.1 | Create `LLMService` class in `tickets/services/llm_service.py` | ⬜ | P0 |
| 5.2 | Design and store classification prompt | ⬜ | P0 |
| 5.3 | Implement Gemini API call with 10s timeout | ⬜ | P0 |
| 5.4 | Parse and validate JSON response against allowed choices | ⬜ | P0 |
| 5.5 | Graceful fallback on API failure / invalid response | ⬜ | P0 |
| 5.6 | Read `GEMINI_API_KEY` from environment variable | ⬜ | P0 |

## Phase 6: Production Hardening
| # | Task | Status | Priority |
|---|------|--------|----------|
| 6.1 | Configure Gunicorn (`gunicorn.conf.py`) with gthread workers | ⬜ | P0 |
| 6.2 | Set `graceful_timeout = 30s`, worker lifecycle hooks | ⬜ | P0 |
| 6.3 | Create `entrypoint.sh` (migrate → collectstatic → exec gunicorn) | ⬜ | P0 |
| 6.4 | Signal forwarding (SIGTERM/SIGINT) in entrypoint | ⬜ | P0 |

## Phase 7: Docker & Infrastructure
| # | Task | Status | Priority |
|---|------|--------|----------|
| 7.1 | Write `backend/Dockerfile` (python:3.12-slim) | ⬜ | P0 |
| 7.2 | Write `frontend/Dockerfile` (multi-stage: node build → nginx serve) | ⬜ | P0 |
| 7.3 | Write `docker-compose.yml` (db, backend, frontend) | ⬜ | P0 |
| 7.4 | Add PostgreSQL healthcheck + `depends_on: condition` | ⬜ | P0 |
| 7.5 | Set `stop_grace_period: 30s` on backend service | ⬜ | P0 |
| 7.6 | Add `nginx.conf` for frontend (static + /api proxy) | ⬜ | P0 |

## Phase 8: React Frontend
| # | Task | Status | Priority |
|---|------|--------|----------|
| 8.1 | Scaffold CRA + Tailwind CSS | ⬜ | P0 |
| 8.2 | Create API layer (`src/api/ticketApi.js`) with Axios | ⬜ | P0 |
| 8.3 | Build `TicketForm` with LLM pre-fill on description blur | ⬜ | P0 |
| 8.4 | Build `TicketList` with `TicketCard` components | ⬜ | P0 |
| 8.5 | Build `FilterBar` (category, priority, status, search) | ⬜ | P0 |
| 8.6 | Build `TicketStatusModal` for status changes | ⬜ | P0 |
| 8.7 | Build `StatsDashboard` with auto-refresh | ⬜ | P0 |
| 8.8 | Wire all components in `App.jsx`, lift refresh state | ⬜ | P0 |

## Phase 9: Final Deliverables
| # | Task | Status | Priority |
|---|------|--------|----------|
| 9.1 | Write `README.md` (setup, LLM rationale, design decisions) | ⬜ | P0 |
| 9.2 | Code review pass — remove dead code, debug prints | ⬜ | P1 |
| 9.3 | End-to-end smoke test via `docker-compose up --build` | ⬜ | P0 |
| 9.4 | Verify incremental commit history (`git log --oneline`) | ⬜ | P1 |

---

## Legend
- ⬜ Not started
- 🔄 In progress  
- ✅ Completed
- ❌ Blocked
