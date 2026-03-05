# Top 200 Questions on the Support Ticket System Project

## 🗄️ Django & Django REST Framework

**1. What version of Django is used in this project and why was it chosen?**
Django 6.0.2 is used. It is a modern, stable release with long-term support offering security patches, ORM improvements, and strong compatibility with Django REST Framework.

**2. What is Django REST Framework (DRF) and why is it used here?**
DRF is a powerful toolkit for building Web APIs on top of Django. It provides serializers, viewsets, authentication, permissions, and browsable API out of the box — reducing boilerplate for the CRUD endpoints in this project.

**3. What are the different settings modules used and why are they split?**
The project uses `base.py`, `development.py`, and `production.py`. Splitting settings keeps environment-specific configuration (DEBUG, CORS, allowed hosts, secret keys) isolated, reducing the risk of accidentally running insecure settings in production.

**4. What is the purpose of `DJANGO_SETTINGS_MODULE` environment variable?**
It tells Django which Python module to load as its settings file. Here it defaults to `config.settings.production`, overriding it to `config.settings.development` enables SQLite and DEBUG mode locally.

**5. What does `DEBUG=False` do in production settings?**
It disables the detailed error pages that expose stack traces, turns off the auto-reloader, and enables stricter security settings like `SECURE_BROWSER_XSS_FILTER`.

**6. What is a Django `ViewSet` and how is it used here?**
A `ViewSet` bundles related view logic for a resource (list, create, retrieve, update) into a single class. `TicketViewSet` uses mixins to allow list, create, retrieve, and partial_update while intentionally excluding DELETE.

**7. Why are PUT and DELETE intentionally excluded from `TicketViewSet`?**
The project specification does not require full replacement of ticket data or hard-deletes. Excluding them enforces that tickets are only updated via PATCH (for status, category, priority) and never deleted.

**8. What is the `partial_update` method and how does it differ from `update`?**
`partial_update` handles PATCH requests, allowing a subset of fields to be updated. `update` handles PUT requests, requiring all fields. Here `partial_update` restricts updates to `status`, `category`, and `priority`.

**9. What does `serializer.is_valid(raise_exception=True)` do?**
It validates incoming data against the serializer's fields and validators. If validation fails, it immediately raises a `ValidationError`, which DRF converts to a `400 Bad Request` response with error details.

**10. What is the role of `read_only_fields` in `TicketSerializer`?**
It prevents clients from setting `id` and `created_at` — these fields are included in responses (read) but ignored if provided in create/update requests (write-protected).

**11. Why is `instance.refresh_from_db()` called after `serializer.save()` in `partial_update`?**
After saving the partial update, the in-memory instance may not reflect DB defaults or auto-computed values. `refresh_from_db()` fetches the latest state from the database before returning the full ticket representation.

**12. What is `APIView` and when is it used instead of a ViewSet?**
`APIView` is the base class for class-based views in DRF, providing HTTP method dispatch (`get`, `post`, etc.). It is used for `StatsView` and `ClassifyView` because they have unique, non-CRUD behavior not suited to a ViewSet.

**13. How does Django's `aggregate()` differ from `annotate()`?**
`aggregate()` computes a single summary value over the entire queryset (e.g., total count). `annotate()` computes a value per row/group and attaches it to each result. `StatsView` uses both — `aggregate()` for total/open counts and `annotate()` for per-priority and per-category breakdowns.

**14. What is `django-filter` and how is it used here?**
`django-filter` provides a `FilterSet` class to declaratively define query parameter filters for DRF viewsets. `TicketFilter` allows filtering tickets by `category`, `priority`, `status`, and full-text `search` via URL parameters.

**15. What is the purpose of the `filterset_class` attribute on `TicketViewSet`?**
It tells DRF's `DjangoFilterBackend` which filter class to use for this viewset. Requests to `GET /api/tickets/?status=open` are automatically processed by `TicketFilter`.

**16. How does full-text search work in the filter?**
It uses `django-filter`'s `CharFilter` with `method='filter_search'` (or similar) that searches across multiple fields using `Q` objects combining `title__icontains` and `description__icontains` with OR logic.

**17. What are Django `TextChoices` and how do they work?**
`TextChoices` is a Django enum subclass for string-valued choices. Each member has a database value (lowercase) and a human-readable label. They replace raw string tuples and provide type-safe constants like `Ticket.Status.OPEN`.

**18. What is `auto_now_add=True` on the `created_at` field?**
It automatically sets the field to the current datetime when the object is first created and makes it uneditable afterwards. It is equivalent to setting the value in `save()` only on creation.

**19. Why does `created_at` have `db_index=True`?**
Tickets are ordered by `-created_at` (newest first). A database index on this column makes ORDER BY queries fast even with millions of rows.

**20. What is the `db_table` Meta option used for?**
It sets the explicit PostgreSQL table name to `tickets` instead of Django's default `appname_modelname` pattern (`tickets_ticket`).

---

## 🗃️ PostgreSQL & Database Design

**21. Why is PostgreSQL 16 used instead of SQLite?**
PostgreSQL supports real CHECK constraints, concurrent connections, full-text search, and production-grade performance. SQLite is single-writer and lacks DB-level constraint enforcement.

**22. What are `CheckConstraint`s and why are they used?**
`CheckConstraint` creates a database-level constraint that rejects any row where the condition is false. Here they enforce that `category`, `priority`, and `status` only ever contain valid values — even if data is inserted via raw SQL, migrations, or direct DB access.

**23. Why is it important to enforce constraints at the DB level rather than just in Django?**
Django ORM validation can be bypassed (raw SQL, bulk inserts, data migrations, external tools). DB-level constraints are the last line of defense and guarantee data integrity regardless of how data enters.

**24. What database indexes are created and why?**
Indexes are created on `category`, `priority`, and `status`. These fields are commonly used in filter queries (`WHERE category = 'billing'`). Indexes make these lookups O(log n) instead of O(n) full table scans.

**25. What is the `ordering` Meta option and what does it do?**
It sets the default ORDER BY clause for all queries on this model. `['-created_at']` means newest tickets first — the minus sign indicates descending order.

**26. How does `Count('id', filter=Q(status='open'))` work?**
It is a conditional aggregate — it counts only rows where `status = 'open'`. Django translates this to a SQL `COUNT(CASE WHEN status = 'open' THEN 1 END)`.

**27. What is `Ticket.objects.earliest('created_at')` used for in `StatsView`?**
It fetches the single ticket with the smallest `created_at` value (the oldest ticket). This is used to calculate how many days the system has been active, which feeds the `avg_tickets_per_day` calculation.

**28. Why is `days_elapsed = max(days_elapsed, 1)` used?**
To avoid division by zero when all tickets were created within the last 24 hours. It ensures the denominator is at least 1, preventing a `ZeroDivisionError`.

**29. What is `values('priority').annotate(count=Count('id'))` doing?**
It groups tickets by `priority` and counts how many tickets exist per group. This is equivalent to `SELECT priority, COUNT(id) FROM tickets GROUP BY priority`.

**30. Why are all priorities initialized to 0 before filling from the query?**
If no tickets exist for a priority (e.g., no `critical` tickets), that priority won't appear in the query results. Pre-initializing ensures the response always contains all four priorities, even if their count is 0.

---

## 🤖 LLM Integration & Classification Pipeline

**31. Why was Google Gemini 1.5 Flash chosen over GPT-4 or Claude?**
Gemini Flash offers a generous free tier with no credit card required, low latency (< 2 s), reliable JSON output, and a simple Python SDK. It is ideal for a portfolio/assessment project where cost and accessibility matter.

**32. What is "few-shot prompting" and how is it implemented here?**
Few-shot prompting provides the model with example input/output pairs before the actual query. Here 5 labelled pairs are embedded in `CLASSIFICATION_PROMPT`, covering billing, technical, account, general, and a critical urgency case.

**33. What is "chain-of-thought" reasoning and what benefit does it provide?**
Chain-of-thought forces the model to reason step-by-step before giving the final answer. Each example includes an "Analysis:" step. This intermediate reasoning reduces misclassification on ambiguous tickets.

**34. What is "keyword pre-extraction" (Signal Injection) and why is it done before the LLM call?**
`_extract_signals()` scans the description with regex patterns and extracts urgency/domain signals. These are injected as a structured hint block at the top of the prompt. The LLM receives pre-labelled hints so it doesn't have to "discover" urgency in ambiguous phrasing.

**35. What urgency patterns does `URGENCY_KEYWORDS` detect?**
It detects: `urgent`, `emergency`, `critical`, `ASAP`, `immediately`, `life-threatening`, `someone can die`, `deadline`, `cannot wait`, `blocking`, `production down`, `data loss`, `security breach`, `outage`, `down`, `right now`, `end of day`.

**36. Why is `temperature=0.05` used in Gemini's `GenerationConfig`?**
Classification is deterministic — there is one correct answer. A near-zero temperature makes the model almost always pick the highest-probability token, giving consistent and reproducible results for the same input.

**37. What is `top_p=0.9` and how does it complement temperature?**
`top_p` (nucleus sampling) restricts token selection to the top tokens whose cumulative probability reaches 90%. Combined with low temperature, it focuses sampling while ignoring very long-tail unlikely tokens.

**38. Why is `max_output_tokens=200` set?**
200 tokens is enough for a brief chain-of-thought analysis plus the JSON output. A cap prevents verbose, rambling responses that consume API quota unnecessarily.

**39. What is `request_options={'timeout': 10}` for?**
It sets a 10-second timeout on the Gemini API call. If the API doesn't respond within 10 seconds, a timeout exception is raised and the keyword heuristic fallback is invoked.

**40. What are the three response shapes `_parse_response()` handles?**
1. Clean JSON (`{"suggested_category": "technical", "suggested_priority": "high"}`)
2. JSON inside a markdown code block (` ```json ... ``` `)
3. Reasoning text followed by JSON (chain-of-thought output)

**41. What regex is used to extract JSON from a reasoning response?**
`r'\{[^{}]*"suggested_category"[^{}]*\}'` — it finds the first JSON object containing the key `suggested_category`, ignoring any surrounding text.

**42. What happens when `json.loads()` fails?**
The function logs a warning with the first 200 characters of the response and returns `DEFAULT_RESPONSE` (`general/medium`) with a `warning` field indicating invalid format.

**43. What is the purpose of `_keyword_fallback()`?**
It classifies tickets using regex keyword scoring when the Gemini API is unavailable or the API key is not set. It counts category keyword matches (scores) and urgency keyword matches, then derives category and priority.

**44. How does the keyword fallback determine priority?**
It checks: (1) extreme words like `die`, `outage`, `breach` → `critical`; (2) ≥ 3 urgency matches → `critical`; (3) ≥ 1 urgency match → `high`; (4) technical failure words → `high`; (5) general category → `low`; else → `medium`.

**45. Why is the keyword fallback "far better than returning `general/medium`"?**
Because it actually analyzes the description. A ticket mentioning "login", "password", "urgent" correctly resolves to `account/high` even without internet access, whereas a static default would always be wrong.

**46. What does `LLMService.classify()` return when the API key is missing?**
It logs a warning and immediately returns the result of `_keyword_fallback(description)` — no `warning` field is added when the key is simply not configured.

**47. What extra field is added to the response when the LLM call fails at runtime?**
A `warning` field is appended to the keyword fallback result, e.g.: `"warning": "LLM unavailable, used keyword analysis: ConnectionError"`.

**48. What is `os.environ.get('GEMINI_API_KEY', '')` doing?**
It safely reads the `GEMINI_API_KEY` environment variable, returning an empty string (falsy) if not set, avoiding a `KeyError`. The empty-string check (`if not api_key:`) then routes to the fallback.

**49. Why is `google.generativeai` imported inside `_call_gemini()` rather than at the top of the file?**
Lazy import avoids importing the `google-generativeai` package when the LLM is not used (e.g., in tests using the keyword fallback). It also keeps the module loadable even if the package is not installed.

**50. What is `genai.GenerativeModel('gemini-1.5-flash')` doing?**
It instantiates a model client for the `gemini-1.5-flash` model variant. This is the "Flash" (speed-optimised) version of Gemini 1.5, as opposed to the larger "Pro" variant.

---

## 🌐 REST API Design

**51. What HTTP methods does the ticket API support?**
- `GET /api/tickets/` — list tickets
- `POST /api/tickets/` — create a ticket
- `GET /api/tickets/<id>/` — retrieve one ticket
- `PATCH /api/tickets/<id>/` — partial update
- `GET /api/tickets/stats/` — statistics
- `POST /api/tickets/classify/` — LLM classification

**52. Why does `POST /api/tickets/` return 201 instead of 200?**
HTTP 201 Created is the semantically correct response code for a successful resource creation. 200 OK indicates a successful general request but does not communicate that a new resource was created.

**53. What does `ClassifyView` return in its response?**
It returns `{"suggested_category": "...", "suggested_priority": "..."}` and optionally a `"warning"` field if the LLM was unavailable. It always returns HTTP 200.

**54. Why is the classify endpoint a separate view rather than part of `TicketViewSet`?**
Classification is a stateless, non-CRUD action that doesn't create or modify any ticket. It is logically separate and implemented as a standalone `APIView` rather than a custom ViewSet action.

**55. What query parameters does `GET /api/tickets/` support?**
`?category=`, `?priority=`, `?status=`, `?search=`. They can be combined (e.g., `?category=technical&status=open&search=crash`).

**56. How are URL patterns registered in this project?**
The project uses DRF's `DefaultRouter` in `tickets/urls.py` to automatically register `TicketViewSet`, and manually adds paths for `StatsView` and `ClassifyView`.

**57. What does the `DefaultRouter` automatically generate?**
It generates URL patterns for the standard actions: `list`, `create`, `retrieve`, `update`, `partial_update`, and `destroy`. Actions not mixed into the ViewSet are simply ignored.

**58. What is the purpose of the `ClassifyRequestSerializer`?**
It validates that the incoming `POST /api/tickets/classify/` body contains a `description` field that is at least 10 characters long and not blank. It strips whitespace before returning the validated value.

**59. What HTTP status code is returned when validation fails?**
`400 Bad Request`, with a JSON body describing which fields failed and why. DRF's `raise_exception=True` handles this automatically.

**60. Why is `description` validated with `min_length=10` in `ClassifyRequestSerializer`?**
Very short descriptions (less than 10 characters) don't provide enough context for accurate classification. The minimum length ensures the LLM and keyword fallback have at least a minimal signal to work with.

---

## 🛡️ Middleware & Error Handling

**61. What does `RequestLoggingMiddleware` log?**
The HTTP method, full path (including query string), response status code, and response time in milliseconds — e.g., `GET /api/tickets/?status=open → 200 (12.3ms)`.

**62. How does `RequestLoggingMiddleware` choose the log level?**
2xx → `INFO`, 4xx → `WARNING`, 5xx → `ERROR`. This makes it easy to find client errors and server errors in log aggregation tools by filtering on level.

**63. Why is `time.monotonic()` used instead of `time.time()` for measuring duration?**
`monotonic()` is guaranteed to never go backwards (unaffected by system clock adjustments). It is the correct choice for measuring elapsed time intervals.

**64. What does `ExceptionHandlingMiddleware.process_exception()` do?**
It catches any exception that escapes the view layer, logs it with full traceback, and returns a structured JSON response instead of Django's HTML traceback page, which would be confusing for API consumers.

**65. Why does the error response include `str(exception)` only in DEBUG mode?**
In production, exception messages may expose internal paths, database schemas, or credentials. Showing only a generic "An unexpected error occurred" prevents information leakage.

**66. What is the order in which Django middleware runs?**
Middleware is executed as a stack: on the request path, middleware runs from top to bottom (as listed in `MIDDLEWARE`). On the response path, it runs from bottom to top. `RequestLoggingMiddleware` wraps the entire request/response cycle.

**67. What is the `get_response` callable in middleware?**
It is the next layer in the middleware chain (or the view function itself if this is the last middleware). Each middleware calls `self.get_response(request)` to pass the request down the chain.

**68. What is the custom DRF exception handler in `exceptions.py`?**
It is a function registered as `EXCEPTION_HANDLER` in DRF settings. It wraps DRF's default handler to ensure all API exceptions return consistent JSON with an `error` key in addition to `detail`.

**69. What happens if `ExceptionHandlingMiddleware` is not present?**
Unhandled exceptions would return Django's HTML 500 page, which is not useful for a JSON API and may expose sensitive debug information.

**70. What does `logger.error(f'...\n{tb}')` accomplish?**
It logs the full Python traceback alongside the error message. This is critical for debugging production issues without exposing the traceback to API consumers.

---

## 🐳 Docker & Infrastructure

**71. What services are defined in `docker-compose.yml`?**
Three services: `db` (PostgreSQL 16), `backend` (Django/Gunicorn), and `frontend` (React/Nginx).

**72. How does the backend wait for the database to be ready?**
`entrypoint.sh` uses a retry loop (up to `MAX_RETRIES=30` attempts, 2-second sleep between each) calling `pg_isready` to check if PostgreSQL is accepting connections before proceeding.

**73. What happens if the database never becomes ready?**
After 30 retries (60 seconds), the script prints a clear error message and exits with `exit 1`, causing the container to stop rather than looping forever.

**74. Why is `exec gunicorn` used instead of `gunicorn` in `entrypoint.sh`?**
`exec` replaces the shell process with Gunicorn, making Gunicorn PID 1 inside the container. Docker's `SIGTERM` on container stop goes directly to Gunicorn for graceful connection draining.

**75. What is the `stop_grace_period: 30s` in `docker-compose.yml`?**
It tells Docker to wait up to 30 seconds for the container to stop after receiving `SIGTERM` before forcefully killing it. This matches Gunicorn's `graceful_timeout` so in-flight requests can complete.

**76. What does the Nginx configuration do in the frontend container?**
It serves the React production build (static files) directly and proxies requests with `/api/` and `/admin/` path prefixes to the backend service on port 8000.

**77. What are Docker healthchecks used for in this project?**
The `db` service has a healthcheck using `pg_isready`. The `backend` service depends on `db` with `condition: service_healthy`, ensuring Django doesn't start until PostgreSQL is ready.

**78. What is `start_period: 15s` in the healthcheck configuration?**
It gives the container 15 seconds to start before health check failures start counting. PostgreSQL needs time to initialize on first boot; without `start_period`, it would fail and restart unnecessarily.

**79. What steps does `entrypoint.sh` perform before starting Gunicorn?**
1. Waits for the database to be ready
2. Runs `python manage.py makemigrations` (creates any pending migrations)
3. Runs `python manage.py migrate` (applies migrations)
4. Runs `python manage.py collectstatic --noinput` (gathers static files)
5. Starts Gunicorn via `exec`

**80. Why is `collectstatic` run in the entrypoint rather than in the Dockerfile?**
Static files may depend on environment-specific settings (STATIC_ROOT). Running at container start ensures the correct settings are applied. Also, the `STATIC_ROOT` directory is often a mounted volume not available during the image build.

**81. What is Gunicorn and why is it used instead of Django's development server?**
Gunicorn is a production-grade WSGI HTTP server that spawns multiple worker processes to handle concurrent requests. Django's `runserver` is single-threaded and not suitable for production traffic.

**82. What does `max_requests=1000` with jitter do in `gunicorn.conf.py`?**
Workers are recycled after handling 1000 requests. The jitter adds a random offset so all workers don't restart simultaneously, preventing request spikes. This combats memory leaks in long-lived workers.

**83. What type of Gunicorn workers are used?**
`gthread` workers — each worker process spawns multiple threads. This allows handling more concurrent connections without spawning as many OS processes, balancing memory usage and concurrency.

**84. What is the default number of Gunicorn workers?**
3, set via the `GUNICORN_WORKERS` environment variable, which defaults to `3` in `gunicorn.conf.py`. A common rule of thumb is `(2 × CPU cores) + 1`.

---

## ⚛️ React Frontend

**85. What React version is used and what is notable about it?**
React 19.2 is used, which includes automatic batching, concurrent features, and the new root API (`ReactDOM.createRoot()`).

**86. What are the six React components in this project?**
`TicketForm`, `TicketList`, `TicketCard`, `FilterBar`, `StatsDashboard`, `LoadingSpinner`. Each has a single responsibility following the Single Responsibility Principle.

**87. What does `TicketForm` do and what makes it special?**
It renders the ticket creation form and implements debounced LLM classification — 1.5 seconds after the user stops typing in the description field, it calls `POST /api/tickets/classify/` and pre-fills the category and priority dropdowns.

**88. What is "debouncing" and why is it used in the classify call?**
Debouncing delays execution until a specified time has passed since the last invocation. It prevents spamming the classify endpoint on every keystroke — the API is only called when the user pauses for 1.5 seconds.

**89. What visual cue tells the user a field was AI-suggested?**
AI-suggested dropdowns are highlighted in blue with the label "(AI suggested — editable)". This makes it clear which fields were auto-filled and that they can be changed.

**90. What is the `refreshKey` pattern used for?**
A state variable (`refreshKey`) is incremented after a ticket is created or updated. Components that depend on the ticket list and stats pass `refreshKey` as a prop/dependency, triggering a re-fetch without a full page reload.

**91. What is the purpose of `FilterBar`?**
It provides dropdowns and a search input for filtering the ticket list by `category`, `priority`, `status`, and a full-text `search` term. Filter inputs are debounced (300 ms) before hitting the API.

**92. What does `StatsDashboard` display?**
Total tickets, open tickets, average tickets per day, a priority breakdown (low/medium/high/critical counts), and a category breakdown (billing/technical/account/general counts).

**93. What library is used for HTTP requests in the frontend?**
Axios, with a pre-configured instance in `src/api/ticketApi.js` that sets the base URL and default headers.

**94. Where are shared constants like category and priority options defined?**
In `src/utils/constants.js`, which exports arrays like `CATEGORIES`, `PRIORITIES`, and `STATUSES` used across multiple components.

**95. How does Tailwind CSS v3 content path configuration work?**
`tailwind.config.js` includes explicit `content` paths (`./src/**/*.{js,jsx}`) so Tailwind's JIT compiler knows which files to scan for class names. Without correct paths, unused CSS would not be purged.

---

## 🧪 Testing

**96. What testing framework is used for the backend?**
Django's built-in `unittest`-based test framework with `TestCase` and `TransactionTestCase`. Tests are run with `python manage.py test`.

**97. What does `test_models.py` cover?**
Ticket model field validation, default values, `__str__` representation, DB-level `CheckConstraint` enforcement, and index creation.

**98. What does `test_views.py` cover?**
All API endpoints: creating tickets (valid/invalid), listing with filters, retrieving single tickets, partial updates, the stats endpoint, and the classify endpoint.

**99. What does `test_llm_service.py` cover?**
16 unit tests covering: JSON parsing for all 3 response shapes, keyword fallback for 8 different description types, signal extraction, and the full `classify()` orchestration with mocked Gemini API.

**100. How is the Gemini API mocked in tests?**
Using `unittest.mock.patch` to replace `LLMService._call_gemini` or `google.generativeai.GenerativeModel.generate_content` with a mock that returns predefined responses without making real API calls.

**101. How do you run the backend tests inside the running Docker container?**
```bash
docker-compose exec backend python manage.py test tickets -v2
```

**102. How do you run tests locally without Docker?**
```bash
cd backend
DJANGO_SETTINGS_MODULE=config.settings.development python manage.py test tickets -v2
```

**103. What does the `-v2` flag do when running Django tests?**
It sets verbosity level 2, printing the name of each test as it runs (PASS/FAIL) instead of just dots.

**104. What database is used during testing?**
Django creates a temporary test database (prefix `test_`) on the configured database engine. In development settings, SQLite is used for speed. In production settings, a separate PostgreSQL test database is created.

**105. Why are tests important for the LLM service specifically?**
The LLM service interacts with an external API that costs money, has rate limits, and produces non-deterministic output. Tests with mocked responses ensure the parsing, validation, and fallback logic work correctly regardless of API availability.

---

## 🔒 Security

**106. What does `DEBUG=False` prevent in production?**
Prevents detailed error tracebacks from being shown to users, disables the development server auto-reloader, and enables security middleware features.

**107. What is `DJANGO_SECRET_KEY` and why must it always be overridden in production?**
It is used for cryptographic signing of cookies, sessions, and CSRF tokens. Using the insecure default key from the repository would allow an attacker to forge signed values.

**108. What CORS (Cross-Origin Resource Sharing) configuration is applied in production?**
Production settings enable strict CORS, restricting which origins can make cross-origin requests to the API. Development allows all origins for convenience.

**109. What are security headers provided by Django production settings?**
Headers like `X-Content-Type-Options`, `X-XSS-Protection`, `Strict-Transport-Security` (HSTS), and `X-Frame-Options` are enabled to protect against common web attacks.

**110. Why are DB credentials set via environment variables rather than hardcoded?**
Hardcoded credentials in source code are a critical security risk — they get committed to version control and are visible to anyone with repository access. Environment variables keep secrets out of code.

**111. How does `ExceptionHandlingMiddleware` improve security?**
In production mode, it hides exception details from the API response, preventing information disclosure of stack traces, file paths, database structures, and other internal details.

**112. What is `.env.example` and how is it used?**
It is a template showing all required environment variables with placeholder values. Developers copy it to `.env` and fill in real values. `.env` is gitignored to prevent secrets from being committed.

**113. Why are database credentials environment-variable-driven in `docker-compose.yml`?**
This allows different credentials in development vs. production without modifying the compose file, and keeps secrets out of version control.

---

## ⚙️ Configuration & Environment

**114. What environment variables does the project require?**
`GEMINI_API_KEY` (recommended), `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`, `GUNICORN_WORKERS`.

**115. What is the default value of `POSTGRES_HOST`?**
`db` — the Docker Compose service name of the PostgreSQL container. Docker Compose creates a DNS entry for each service using its name.

**116. What is `DJANGO_ALLOWED_HOSTS` and when does it matter?**
It is a list of host/domain names Django is allowed to serve. It prevents HTTP Host header attacks. In production it must be set to the actual domain/IP of the server.

**117. How does the `.env` file get loaded in Docker Compose?**
Docker Compose automatically reads a `.env` file in the same directory and makes its variables available to substitute in `docker-compose.yml` using `${VARIABLE}` syntax.

**118. What happens if `GEMINI_API_KEY` is not set?**
The application is fully functional. Ticket creation and management work normally. LLM classification silently falls back to the keyword heuristic instead.

---

## 🏗️ Architecture & Design Decisions

**119. Why is `LLMService` decoupled from Django views?**
Decoupling makes it independently testable (no Django test client needed), swappable (can replace Gemini with another provider by changing only this class), and reusable from management commands or tasks.

**120. What is the "service layer" pattern?**
Business logic (like LLM classification) is extracted from views into a dedicated service class. Views remain thin (request/response handling only) and services contain the domain logic.

**121. Why does `StatsView` use database-level aggregation instead of Python loops?**
Database aggregation is orders of magnitude faster for large datasets. Python loops require fetching all rows into memory, then iterating. SQL `COUNT`, `GROUP BY`, and `annotate` push computation to the database engine.

**122. What design principle does the frontend's 6-component structure follow?**
The Single Responsibility Principle — each component has one reason to change. `TicketCard` handles display, `FilterBar` handles filtering, `StatsDashboard` handles statistics display, etc.

**123. Why is React's build served by Nginx rather than Django's development server?**
Django's `staticfiles` server is not production-safe. Nginx is a high-performance, purpose-built static file server. Serving assets from Nginx eliminates load on Django/Gunicorn.

**124. Why is the system designed to "never block ticket creation" during LLM failures?**
User experience: if the LLM is down, users should still be able to submit tickets. The classification suggestion is a convenience feature, not a hard requirement for ticket creation.

---

## 🔁 Data Flow & Request Lifecycle

**125. What is the end-to-end flow when a user submits a new ticket?**
1. React form sends `POST /api/tickets/` with title, description, category, priority
2. Nginx proxies to Django/Gunicorn
3. `RequestLoggingMiddleware` records the start time
4. DRF routes to `TicketViewSet.create()`
5. `TicketSerializer` validates the data
6. Django ORM saves to PostgreSQL
7. 201 response returned
8. React refreshes the ticket list and stats

**126. What is the flow when a user types in the description field?**
1. `onChange` fires on every keystroke
2. Debounce timer resets on each keystroke
3. After 1.5 s of no input, `classifyTicket(description)` is called
4. `POST /api/tickets/classify/` is sent to the backend
5. `LLMService.classify()` runs
6. Suggested category and priority are returned
7. React pre-fills and highlights the dropdowns in blue

**127. What happens when a ticket's status is updated via PATCH?**
1. React sends `PATCH /api/tickets/<id>/` with `{"status": "resolved"}`
2. `TicketViewSet.partial_update()` is called
3. `TicketUpdateSerializer` validates only the provided fields
4. Django ORM updates the record
5. `refresh_from_db()` fetches the latest state
6. Full `TicketSerializer` response is returned
7. React's `refreshKey` increments, re-fetching the list and stats

---

## 📦 Dependencies & Requirements

**128. What are the key Python packages in `requirements.txt`?**
`django`, `djangorestframework`, `django-filter`, `psycopg2-binary` (PostgreSQL adapter), `gunicorn`, `google-generativeai`, `django-cors-headers`.

**129. What is `psycopg2-binary` and why is it used?**
It is the PostgreSQL database adapter for Python. The `-binary` variant includes pre-compiled binaries, avoiding the need to compile from source during Docker image build.

**130. What is `django-cors-headers` used for?**
It adds CORS headers to Django responses, allowing the React frontend (on a different port in development) to make cross-origin API requests without being blocked by browsers.

**131. Why is `gunicorn` a production dependency but not needed for running tests?**
Tests use Django's test runner which doesn't need an HTTP server. Gunicorn is only needed to serve the application in production.

**132. What is `google-generativeai`?**
Google's official Python SDK for the Gemini API. It handles authentication, request formatting, response parsing, and retry logic for Gemini API calls.

---

## 🔍 Filtering & Search

**133. How are multiple filters combined in the ticket list?**
Django's `Q` objects with AND logic combine filter conditions. A request like `?category=technical&status=open` generates `WHERE category='technical' AND status='open'`.

**134. How does the search filter work across multiple fields?**
The search filter uses `Q(title__icontains=term) | Q(description__icontains=term)` — a case-insensitive OR search across both the title and description fields.

**135. What is `icontains` in Django ORM?**
It is a case-insensitive `LIKE '%term%'` lookup. It finds rows where the field contains the search term regardless of case.

**136. Why is the search debounced at 300 ms in the frontend?**
To avoid making an API request on every keystroke. 300 ms is a common UX-friendly delay that feels responsive while significantly reducing API calls during fast typing.

---

## 🚀 Deployment & Operations

**137. How is the full stack started with one command?**
```bash
docker-compose up --build
```

**138. What services are accessible after deployment?**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/tickets/`
- Django Admin: `http://localhost:8000/admin/`

**139. How are database migrations managed?**
They are applied automatically in `entrypoint.sh` via `python manage.py migrate`. `makemigrations` is also run automatically to create migrations from any new model changes.

**140. What is the Django Admin and how is it accessed?**
Django Admin is an auto-generated web interface for managing model data. It is available at `/admin/` and requires a superuser account created with `python manage.py createsuperuser`.

**141. How do you rebuild just the backend container after a code change?**
```bash
docker-compose up --build backend
```

**142. How would you check the backend application logs?**
```bash
docker-compose logs -f backend
```

**143. What is `--no-pager` used for when running Git commands inside the container?**
It prevents interactive paging output, making output non-interactive and suitable for scripted environments.

---

## 🧠 Advanced Topics

**144. What is a "defence-in-depth" strategy and how is it applied here?**
Multiple layers of protection: DB-level constraints, DRF serializer validation, middleware exception handling, structured error responses, environment variable secrets. No single layer is relied upon exclusively.

**145. What is Gunicorn's `graceful_timeout`?**
The time Gunicorn gives in-flight requests to complete before forcefully terminating workers. Set to 30 s here, matching Docker's `stop_grace_period`.

**146. What is a "zero-downtime deployment" and is it supported here?**
Zero-downtime deployment keeps the application serving traffic while new code is deployed. This project doesn't implement rolling updates — `docker-compose up --build` causes a brief downtime during restart.

**147. How does the `refreshKey` pattern avoid re-rendering the entire React app?**
Only components that receive `refreshKey` as a prop or hook dependency re-fetch data. Other parts of the UI are unaffected, avoiding unnecessary renders.

**148. What is the purpose of `db_index=True` on `created_at`?**
Since tickets are ordered by `created_at` descending on every list request, an index on this column speeds up the `ORDER BY` operation significantly.

**149. How does the system handle concurrent ticket submissions?**
PostgreSQL handles concurrency at the database level with row-level locking and transactions. Gunicorn's multiple workers handle concurrent HTTP requests. Django ORM operations within a request are atomic unless explicitly wrapped.

**150. What would happen if two users tried to update the same ticket simultaneously?**
The last write wins. Since `partial_update` fetches the instance, validates, and saves in the same request, there is no optimistic locking — a concurrent update between the fetch and save would be overwritten. Adding `updated_at` and comparing versions would be needed for proper conflict resolution.

---

## 📊 Statistics & Analytics

**151. What metrics does the `GET /api/tickets/stats/` endpoint return?**
`total_tickets`, `open_tickets`, `avg_tickets_per_day`, `priority_breakdown` (dict of counts per priority), `category_breakdown` (dict of counts per category).

**152. How is `avg_tickets_per_day` calculated?**
`total_tickets / days_elapsed`, where `days_elapsed` is the number of days between the oldest ticket's `created_at` and now, with a minimum of 1 day.

**153. Why is a minimum of 1 day enforced in `days_elapsed`?**
To prevent division by zero when all tickets were created in the last 24 hours. It also prevents inflated averages (e.g., if 10 tickets were created 2 hours ago, the average shouldn't show as 120/day).

**154. Why are statistics computed at the database level?**
Database engines are highly optimized for aggregate queries. Computing counts and groupings in Python would require loading all ticket rows into memory, which scales poorly with large datasets.

**155. What is `Count('id')` vs `Count('*')` in Django ORM?**
`Count('id')` counts non-null values of the `id` column. `Count('*')` counts all rows including nulls. Since `id` is a primary key (never null), both give the same result. `Count('id')` is idiomatic in Django.

---

## 🌍 Internationalization & Localization

**156. What timezone is used for `created_at` timestamps?**
Django stores all `DateTimeField` values in UTC when `USE_TZ=True`. `timezone.now()` returns the current UTC time, used for the `avg_tickets_per_day` calculation.

**157. Why is `timezone.now()` preferred over `datetime.now()`?**
`timezone.now()` returns a timezone-aware datetime in UTC when `USE_TZ=True`. `datetime.now()` returns a naive datetime in the local server timezone, which can cause subtle bugs in date comparisons.

---

## 📝 Serializer Validation

**158. What field-level validators are defined in `TicketSerializer`?**
`validate_title()` strips whitespace and raises `ValidationError` if the result is empty. `validate_description()` does the same. Both prevent titles/descriptions consisting only of whitespace.

**159. What is the difference between field-level and object-level validation in DRF?**
Field-level (`validate_<field>()`) validates a single field in isolation. Object-level (`validate()`) receives all fields after individual validation and can check cross-field constraints (e.g., field A must be consistent with field B).

**160. Why does `TicketUpdateSerializer` not include `title` and `description`?**
These fields are immutable after creation — the spec says only `status`, `category`, and `priority` can be changed via PATCH. Excluding them from the serializer prevents accidental or malicious modification.

---

## 🖥️ Frontend State Management

**161. Why is React's built-in `useState` used instead of Redux or Zustand?**
The application state is simple — ticket list, filters, and a refresh counter. A global state library would add complexity without benefit for this scale of app.

**162. What does the `useEffect` hook do when `refreshKey` changes?**
It triggers a re-fetch of the ticket list from `GET /api/tickets/` with the current filter parameters. The ticket data displayed updates without a page reload.

**163. How does the filter state flow from `FilterBar` to `TicketList`?**
Filter values are stored in the parent component (`App.js`) as state. They are passed down to `FilterBar` as props with callback setters, and also passed to `TicketList` which uses them as query parameters.

---

## 🔧 Practical & Operational Questions

**164. How would you add a new ticket category (e.g., "security")?**
1. Add `SECURITY = 'security', 'Security'` to `Ticket.Category`
2. Update the `valid_category` `CheckConstraint` to include `'security'`
3. Add security keyword patterns to `CATEGORY_SIGNALS` in `llm_service.py`
4. Update the classification prompt table
5. Create a new Django migration
6. Update frontend constants

**165. How would you add authentication to the API?**
Add DRF's `TokenAuthentication` or `JWTAuthentication` to `DEFAULT_AUTHENTICATION_CLASSES` in settings, add `IsAuthenticated` to `DEFAULT_PERMISSION_CLASSES`, and create user registration/login endpoints.

**166. How would you add pagination to the ticket list?**
Add `DEFAULT_PAGINATION_CLASS` and `PAGE_SIZE` to DRF settings in `settings/base.py`. DRF will automatically paginate list responses.

**167. How would you add an email notification when a ticket's status changes?**
Override `TicketViewSet.partial_update()` to detect status changes and send email via Django's `send_mail()` or a task queue like Celery.

**168. How would you replace Gemini with a different LLM provider?**
Modify only `LLMService._call_gemini()` — replace the `google.generativeai` calls with the new provider's SDK while keeping the same input/output interface. The rest of the pipeline is unchanged.

**169. How would you scale this application to handle 10,000 tickets per day?**
- Add read replicas for the PostgreSQL database
- Increase `GUNICORN_WORKERS`
- Add a Redis cache for stats (cache for 60 seconds)
- Use Celery + Redis for async LLM classification
- Add a CDN for static assets

**170. How would you add rate limiting to the classify endpoint?**
Use `django-ratelimit` or DRF's `UserRateThrottle`/`AnonRateThrottle` to limit classify calls per IP/user per minute.

---

## 🧩 Miscellaneous

**171. What does `__str__` return for a Ticket instance?**
`[<Priority>] <Title>`, e.g., `[Critical] Production database is down`. The `get_priority_display()` method returns the human-readable label from `TextChoices`.

**172. What is `verbose_name_plural` in the Meta class?**
It sets the plural display name used in the Django Admin and `verbose_name` responses. Without it, Django auto-pluralizes (e.g., "Ticketss" — wrong). Here it is set to `'Tickets'`.

**173. What is `apps.py` used for in Django?**
It defines the application configuration class (`TicketsConfig`). The `name` and `verbose_name` attributes identify the app. It can also hold the `ready()` method for app startup signals.

**174. What is `admin.py` used for?**
Registering models with the Django Admin interface. Models registered here appear in the `/admin/` panel.

**175. Why is the Gemini SDK imported lazily inside `_call_gemini()`?**
To avoid a hard dependency on the package when the LLM is not configured. The keyword fallback runs without it, and tests can mock the classify method at a higher level.

**176. What would happen if `URGENCY_KEYWORDS` regex compilation failed?**
The module would fail to import (`re.compile()` raises `re.error` on invalid patterns), crashing the Django startup. Regex patterns should be tested during development.

**177. How is the `docs` folder used in this project?**
It contains design documents (`DESIGN.md`) and task descriptions (`TASKS.md`). It serves as project documentation for developers and assessors.

**178. What is `problem_statement.md` at the root of the project?**
It documents the original problem statement for the assessment — the issue that drove the LLM optimization work (misclassification of "someone can die" tickets as `medium` priority).

**179. What does the `Tech_Intern_Assessment.pdf` contain?**
The original assessment brief describing the requirements for the support ticket system, including the AI classification feature, API endpoints, and deployment requirements.

**180. What is `gunicorn.conf.py` for?**
It is Gunicorn's configuration file. It sets the number of workers, worker class (`gthread`), threads per worker, `max_requests`, `graceful_timeout`, and logging configuration.

**181. What is the purpose of `.gitattributes`?**
It controls how Git handles line endings (`text=auto`) and diff algorithms for specific file types. It ensures consistent line endings across Windows and Unix developers.

**182. Why is `blank=False` set explicitly on `title` and `description`?**
While `blank=False` is the default, it is set explicitly for clarity. It ensures DRF serializer validation rejects empty strings, complementing the ORM-level constraint.

**183. What is `help_text` on model fields used for?**
It provides human-readable descriptions in the Django Admin interface and in DRF's browsable API. It also serves as documentation for developers reading the model code.

**184. How does the `refreshKey` pattern compare to React Query or SWR?**
`refreshKey` is a manual, simple refetch trigger. React Query/SWR offer automatic refetching, caching, deduplication, and stale-while-revalidate patterns — far more powerful but adding complexity. `refreshKey` is appropriate for this project's scale.

**185. What is `postcss.config.js` for?**
It configures PostCSS, the CSS preprocessor. Here it registers Tailwind CSS and Autoprefixer as PostCSS plugins, enabling Tailwind's JIT compilation and adding vendor prefixes for browser compatibility.

**186. What is the `nginx.conf` file responsible for?**
Nginx configuration for the frontend container: static file serving from `/usr/share/nginx/html`, gzip compression, cache headers for static assets, and proxy rules forwarding `/api/` and `/admin/` to the backend.

**187. How does Nginx know to proxy `/api/` requests to the Django backend?**
The `nginx.conf` contains a `location /api/` block with `proxy_pass http://backend:8000;`. Docker Compose's internal DNS resolves `backend` to the Django container's IP.

**188. What is the `.dockerignore` file for?**
It tells Docker which files/directories to exclude from the build context. This speeds up builds and prevents secrets (`.env`), development dependencies (`node_modules`), and version control (`.git`) from being copied into the image.

**189. What would you change to make the LLM classification asynchronous?**
Move the `POST /api/tickets/classify/` call to a Celery task. The ticket creation endpoint would immediately return 201, and classification would update the ticket's category/priority in the background via a PATCH.

**190. How does the application handle a completely empty ticket list?**
`StatsView` returns `total_tickets: 0`, `open_tickets: 0`, `avg_tickets_per_day: 0.0`, and all breakdown counts as 0. The `if total_tickets > 0:` guard prevents the `earliest()` query and division from running.

**191. What would you monitor in production for this application?**
- Response times (p95, p99 latency)
- Error rates (4xx, 5xx per minute)
- LLM API call success rate and latency
- Database connection pool utilization
- Container CPU and memory usage
- Ticket creation rate

**192. What logging configuration does the project use?**
It uses Python's `logging` module with a named logger `'tickets'`. Log levels: DEBUG (development), INFO (production for normal requests). Gunicorn has its own access and error log configuration.

**193. What is the purpose of `db_index=True` on `created_at` vs. the explicit `indexes` in Meta?**
`db_index=True` on the field creates a standard B-tree index. The `indexes` list in `Meta` creates named indexes on `category`, `priority`, and `status` allowing for custom names (important for migrations) and potentially composite indexes.

**194. How would you add a "assigned to" field linking tickets to users?**
Add a `ForeignKey` to Django's `User` model: `assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)`. Create a migration and update serializers.

**195. How does the `TicketCard` component handle status updates?**
It renders a dropdown for status with an `onChange` handler that calls `PATCH /api/tickets/<id>/` via the ticketApi module, then invokes a callback to trigger `refreshKey` increment.

**196. What is the `LoadingSpinner` component?**
A simple animated spinner shown while API requests are in progress. It is conditionally rendered in `TicketList` and `StatsDashboard` based on a `loading` state boolean.

**197. What determines the ordering of tickets in the API response?**
The `Meta.ordering = ['-created_at']` on the `Ticket` model sets the default ordering. Newest tickets appear first. This can be overridden by explicitly passing `?ordering=` query parameters if `OrderingFilter` is configured.

**198. Why is the frontend container separate from the backend container?**
Separation of concerns and independent scaling. The frontend (static files) can be served by many Nginx replicas independently of the backend API. It also allows each service to use its own base image optimized for its role.

**199. How would you implement ticket deletion (soft delete)?**
Add a `deleted_at = models.DateTimeField(null=True, blank=True)` field, override the model's `delete()` method to set this field instead of removing the row, and add `.filter(deleted_at__isnull=True)` to the default queryset manager.

**200. What is the key design lesson of this project regarding LLM classification?**
Never rely on a single classification strategy. The layered approach — few-shot prompting, chain-of-thought, signal extraction, validation, and keyword fallback — ensures the system is robust, accurate, and never blocking. Accuracy comes from explicit signal injection; resilience comes from graceful fallbacks.
