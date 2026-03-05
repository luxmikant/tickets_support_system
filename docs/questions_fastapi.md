# Top 100 Questions on FastAPI

## 🚀 Core Concepts & Introduction

**1. What is FastAPI and what makes it different from Flask or Django REST Framework?**
FastAPI is a modern, high-performance Python web framework for building APIs. It differs from Flask (no built-in data validation, no async-first design) and DRF (less boilerplate, automatic OpenAPI docs, native Pydantic integration). FastAPI is built on Starlette (ASGI) and Pydantic, giving it async-first architecture and automatic data validation.

**2. What is ASGI and how does it differ from WSGI?**
ASGI (Asynchronous Server Gateway Interface) is a standard interface between async-capable Python web frameworks and servers. WSGI is synchronous — one request is handled at a time per worker. ASGI supports async handlers, WebSockets, HTTP/2, and long-lived connections. FastAPI uses ASGI via Starlette; Django/DRF uses WSGI by default.

**3. What are Uvicorn and Gunicorn and how are they used with FastAPI?**
Uvicorn is a lightning-fast ASGI server. Gunicorn is a production-grade WSGI/ASGI process manager. In production, Gunicorn spawns multiple Uvicorn workers: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`. This combines Gunicorn's process management with Uvicorn's async performance.

**4. What is Pydantic and why is it central to FastAPI?**
Pydantic is a data validation library using Python type annotations. FastAPI uses Pydantic models for request body validation, response serialization, dependency injection types, and schema generation. It provides automatic validation, type coercion, and JSON serialization with clear error messages.

**5. How does FastAPI generate interactive API documentation automatically?**
FastAPI inspects route function signatures, type annotations, and Pydantic models to generate an OpenAPI 3.0 schema. It then serves this schema as interactive Swagger UI at `/docs` and ReDoc at `/redoc` — no additional configuration needed.

**6. What is the minimum code to create a working FastAPI application?**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```
Run with: `uvicorn main:app --reload`

**7. What does `--reload` do when running Uvicorn?**
It enables hot-reloading — Uvicorn watches source files and automatically restarts the server when code changes. Used only in development; never in production (overhead and potential race conditions).

**8. What is the `status_code` parameter on route decorators?**
It sets the default HTTP response status code for that endpoint. Example: `@app.post("/items/", status_code=201)` returns 201 Created. The default is 200 OK.

---

## 📦 Path Operations & Routing

**9. What are "path operations" in FastAPI?**
Path operations are route handlers — functions decorated with HTTP method decorators (`@app.get`, `@app.post`, `@app.put`, `@app.patch`, `@app.delete`) mapped to URL paths.

**10. How do you define path parameters?**
Use curly braces in the path and a matching parameter name with type annotation:
```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```
FastAPI automatically validates and converts `item_id` to `int`.

**11. How do you define query parameters?**
Any function parameter not in the path template is treated as a query parameter:
```python
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10):
    return items[skip: skip + limit]
```
Accessed via `/items/?skip=0&limit=10`.

**12. How do you make a query parameter optional with a default value vs. required?**
Default value → optional: `def get(q: str = None)` or `def get(q: Optional[str] = None)`.
No default → required: `def get(q: str)`.
Using `Query()`: `def get(q: str = Query(default=None, min_length=3))`.

**13. What is the `Query` class and when is it used?**
`Query` adds metadata and validation to query parameters: min/max length, regex patterns, deprecation flags, aliases, and documentation. Example:
```python
from fastapi import Query
def search(q: str = Query(default=None, min_length=3, max_length=50)):
```

**14. What is the `Path` class and when is it used?**
Similar to `Query`, `Path` adds validation and metadata to path parameters. Example:
```python
from fastapi import Path
def get_item(item_id: int = Path(ge=1, le=1000)):
```

**15. How do you include multiple routers in a FastAPI application?**
Use `APIRouter` in submodules and `app.include_router()` in the main app:
```python
from fastapi import APIRouter
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def list_items(): ...

# In main.py:
app.include_router(router)
```

**16. What is the `prefix` parameter on `APIRouter`?**
It prepends a path prefix to all routes in the router. `prefix="/items"` means `@router.get("/")` maps to `/items/` and `@router.get("/{id}")` maps to `/items/{id}`.

**17. What are `tags` on routes and routers used for?**
Tags group related endpoints in the auto-generated OpenAPI documentation. Endpoints with `tags=["items"]` appear under the "items" section in Swagger UI.

**18. How does FastAPI handle conflicting routes (e.g., `/items/latest` vs `/items/{item_id}`)?**
Routes are evaluated in definition order. Define static routes before parameterized ones to ensure `/items/latest` is matched before `/items/{item_id}` tries to parse "latest" as an `item_id`.

---

## 🔍 Request Body & Pydantic Models

**19. How do you define a request body with a Pydantic model?**
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.post("/items/")
def create_item(item: Item):
    return item
```
FastAPI reads the JSON body, validates it against `Item`, and passes a typed instance.

**20. How do you add validation to Pydantic fields?**
Use `Field()` with validators:
```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Must be positive")
```

**21. What Pydantic validators are available?**
`gt` (greater than), `ge` (≥), `lt` (less than), `le` (≤), `min_length`, `max_length`, `pattern` (regex), `example`. For custom logic, use `@field_validator` (Pydantic v2) or `@validator` (Pydantic v1).

**22. How do you define a response model in FastAPI?**
Use the `response_model` parameter:
```python
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int): ...
```
FastAPI filters the response through `ItemResponse`, excluding fields not in the model and validating output.

**23. Why use `response_model` instead of just returning a dict?**
`response_model` provides automatic output validation, field filtering (e.g., hiding `password` from responses), JSON serialization, and OpenAPI schema generation for the response.

**24. What is `response_model_exclude_unset`?**
When `True`, fields not explicitly set in the returned model are excluded from the response. Useful for partial updates — only changed fields are returned.
```python
@app.patch("/items/{id}", response_model=Item, response_model_exclude_unset=True)
```

**25. How do you accept both path parameters and a request body?**
```python
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}
```
FastAPI correctly identifies `item_id` as path and `item` as body.

**26. What is `model_config` / `class Config` in Pydantic models?**
Configuration class controlling model behavior: `from_attributes=True` (allow ORM objects as input), `str_strip_whitespace=True` (auto-strip strings), `populate_by_name=True` (allow field name or alias).

**27. How do you handle nested Pydantic models?**
Define child models and reference them in parent models:
```python
class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    name: str
    address: Address
```
FastAPI validates nested structures automatically.

---

## 🔗 Dependency Injection

**28. What is FastAPI's dependency injection system?**
A powerful mechanism for declaring shared logic (database connections, auth, query parsing) as reusable callables. FastAPI resolves dependencies automatically and injects their return values into path operation functions.

**29. How do you create and use a dependency?**
```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

**30. What is a "yield dependency" and what is it used for?**
A dependency that uses `yield` acts like a context manager — code before `yield` runs before the handler, and code after `yield` runs after the response (for cleanup). Used for database sessions, file handles, and resource management.

**31. Can dependencies be nested?**
Yes. A dependency can itself declare dependencies via `Depends()`. FastAPI builds a dependency graph and resolves them in order, caching each dependency by default within the same request.

**32. What is `Depends()` with `use_cache=False`?**
By default, a dependency called multiple times in the same request is executed once (cached). `Depends(my_dep, use_cache=False)` forces it to execute on every call.

**33. How do you create a reusable dependency class (callable)?**
```python
class PaginationParams:
    def __init__(self, skip: int = 0, limit: int = 10):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
def list_items(pagination: PaginationParams = Depends()):
    return items[pagination.skip:][:pagination.limit]
```

**34. What is `Security()` vs `Depends()` in FastAPI?**
`Security()` is a subclass of `Depends()` specifically for security/authentication. It supports `scopes` for OAuth2 scope-based authorization and appears distinctly in the OpenAPI schema.

---

## 🔐 Authentication & Security

**35. How does FastAPI implement HTTP Basic Auth?**
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.get("/protected")
def protected(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin":
        raise HTTPException(status_code=401)
    return {"user": credentials.username}
```

**36. How does FastAPI implement Bearer Token authentication?**
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.get("/protected")
def protected(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    # validate token...
```

**37. How is OAuth2 with Password flow implemented in FastAPI?**
Use `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm`. The login endpoint accepts form data, validates credentials, and returns a JWT token. Protected endpoints use `Depends(oauth2_scheme)` to extract and validate the token.

**38. How do you create and verify JWT tokens in FastAPI?**
Use the `python-jose` library:
```python
from jose import jwt, JWTError

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**39. How do you add CORS support to FastAPI?**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**40. What is `HTTPException` and how is it raised?**
```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="Item not found")
```
FastAPI converts this to a JSON error response with the specified status code and a body `{"detail": "Item not found"}`.

---

## ⚡ Async & Performance

**41. When should you use `async def` vs `def` for route handlers?**
Use `async def` when the handler performs I/O-bound operations (database queries, external API calls, file reads) using `await`. Use `def` for CPU-bound operations — FastAPI runs sync functions in a thread pool to avoid blocking the event loop.

**42. What happens if you use a blocking call (e.g., `time.sleep()`) inside `async def`?**
It blocks the entire event loop, preventing other requests from being processed. Use `await asyncio.sleep()` instead, or run blocking code with `await asyncio.run_in_executor(None, blocking_func)`.

**43. What is `BackgroundTasks` in FastAPI?**
A mechanism to run tasks after the response is sent, without blocking the response:
```python
from fastapi import BackgroundTasks

def send_email(email: str): ...

@app.post("/signup/")
def signup(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Registered"}
```

**44. How does FastAPI achieve high performance?**
- ASGI (async-first, non-blocking I/O)
- Pydantic v2 (Rust-powered validation)
- Starlette's efficient request handling
- No ORM overhead by default
- Benchmarks comparable to NodeJS and Go for async I/O workloads

**45. What is a lifespan event handler in FastAPI?**
Lifespan events run code on application startup and shutdown using an async context manager:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to DB, load ML models
    yield
    # Shutdown: close connections, save state

app = FastAPI(lifespan=lifespan)
```

---

## 🗄️ Database Integration

**46. How do you integrate SQLAlchemy with FastAPI?**
Create a `database.py` with engine, `SessionLocal`, and `Base`. Use a `get_db` yield dependency to provide sessions to routes. Models inherit from `Base`.

**47. What is SQLAlchemy's `SessionLocal`?**
A session factory created with `sessionmaker(bind=engine)`. Each call creates a new database session. In FastAPI, one session per request is the standard pattern.

**48. How do you use SQLAlchemy async sessions with FastAPI?**
Use `create_async_engine` and `AsyncSession` from `sqlalchemy.ext.asyncio`:
```python
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession)
```

**49. What is Alembic and how does it relate to FastAPI?**
Alembic is SQLAlchemy's database migration tool. FastAPI doesn't include migrations, so Alembic fills the same role as Django migrations — tracking schema changes and applying them incrementally.

**50. How do you use Tortoise ORM or SQLModel with FastAPI?**
`SQLModel` (by FastAPI's author) combines Pydantic and SQLAlchemy — models serve as both Pydantic schemas and SQLAlchemy ORM models, reducing duplication:
```python
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
```

---

## 📄 File Upload & Forms

**51. How do you handle file uploads in FastAPI?**
```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

**52. How do you handle form data in FastAPI?**
```python
from fastapi import Form

@app.post("/login/")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```
Note: Cannot use both `Form` and JSON body in the same request.

**53. How do you validate file types or sizes in FastAPI?**
Check `file.content_type` for MIME type and `file.size` (if available) or read content and check `len(content)` after reading. Raise `HTTPException(400)` if invalid.

---

## 📡 WebSockets

**54. How do you create a WebSocket endpoint in FastAPI?**
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        await ws.send_text(f"Echo: {data}")
```

**55. How do you broadcast messages to multiple WebSocket clients?**
Maintain a list of active connections and iterate over them to send messages:
```python
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def broadcast(self, message: str):
        for ws in self.active:
            await ws.send_text(message)
```

---

## 🧪 Testing

**56. How do you test FastAPI endpoints?**
Use `TestClient` from `starlette.testclient`:
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

**57. How do you test async FastAPI endpoints?**
Use `httpx.AsyncClient` with `pytest-asyncio`:
```python
import pytest
import httpx

@pytest.mark.anyio
async def test_create_item():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/items/", json={"name": "Test", "price": 9.99})
    assert response.status_code == 201
```

**58. How do you override dependencies in tests?**
Use `app.dependency_overrides`:
```python
def override_get_db():
    yield test_db_session

app.dependency_overrides[get_db] = override_get_db
```
This replaces the real DB dependency with a test database session.

**59. How do you test endpoints that require authentication?**
Override the auth dependency to return a mock user, or pass valid authentication headers:
```python
app.dependency_overrides[get_current_user] = lambda: {"id": 1, "name": "Test User"}
```

**60. What is `pytest.fixture` and how is it used with FastAPI tests?**
Fixtures provide reusable setup/teardown for tests. A database fixture creates a test DB, creates tables, yields the session, and rolls back after the test:
```python
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
```

---

## 📘 OpenAPI & Documentation

**61. How do you add a description to an endpoint in FastAPI?**
Use the function's docstring:
```python
@app.get("/items/{id}")
def get_item(id: int):
    """
    Retrieve an item by its unique ID.

    - **id**: The item's integer identifier
    """
```

**62. How do you add examples to the OpenAPI schema?**
Use `openapi_examples` in `Body()` or `example` in Pydantic `Field()`:
```python
class Item(BaseModel):
    name: str = Field(example="Laptop")
    price: float = Field(example=999.99)
```

**63. How do you hide an endpoint from the OpenAPI docs?**
```python
@app.get("/internal/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}
```

**64. How do you customize the OpenAPI metadata (title, version, description)?**
```python
app = FastAPI(
    title="My API",
    version="1.0.0",
    description="A description of my API",
    contact={"name": "Support", "email": "support@example.com"},
    license_info={"name": "MIT"},
)
```

**65. How do you add a custom OpenAPI tags metadata?**
```python
tags_metadata = [
    {"name": "items", "description": "Operations with items"},
    {"name": "users", "description": "User management"},
]
app = FastAPI(openapi_tags=tags_metadata)
```

---

## ⚙️ Middleware & Event Handling

**66. How do you add custom middleware to FastAPI?**
```python
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        print(f"{request.method} {request.url} → {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)
```

**67. What is the `Request` object in FastAPI/Starlette?**
It represents the incoming HTTP request. Access headers (`request.headers`), body (`await request.body()`), JSON (`await request.json()`), cookies (`request.cookies`), client IP (`request.client.host`), and URL parameters.

**68. How do you access request headers in a path operation?**
Declare a `Header` parameter:
```python
from fastapi import Header

@app.get("/items/")
def list_items(x_token: str = Header(...)):
    return {"token": x_token}
```
FastAPI converts `x_token` to the `X-Token` header (underscore to hyphen).

**69. How do you set response headers?**
Use `Response` as a parameter or return a `Response` object:
```python
from fastapi import Response

@app.get("/items/")
def list_items(response: Response):
    response.headers["X-Custom-Header"] = "value"
    return items
```

**70. How do you set and read cookies in FastAPI?**
Set: `response.set_cookie(key="session", value="abc123", httponly=True)`
Read: `def get(session: str = Cookie(default=None)):`

---

## 🔄 Error Handling

**71. How do you create a global exception handler?**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
```

**72. What is `RequestValidationError` and how do you customize its response?**
It is raised when request data fails Pydantic validation. Override its handler to customize the 422 response format:
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    return JSONResponse(status_code=400, content={"errors": exc.errors()})
```

**73. How do you raise a 422 Unprocessable Entity error manually?**
```python
from fastapi import HTTPException
raise HTTPException(status_code=422, detail=[{"loc": ["body", "price"], "msg": "Must be positive"}])
```
Or let Pydantic validation automatically raise it.

**74. What is the difference between `HTTPException` and `RequestValidationError`?**
`HTTPException` is manually raised in application code (e.g., 404, 403). `RequestValidationError` is automatically raised by Pydantic when request data is invalid. They have different default handlers.

---

## 📊 Response Types

**75. What response types does FastAPI support?**
`JSONResponse` (default), `HTMLResponse`, `PlainTextResponse`, `FileResponse`, `StreamingResponse`, `RedirectResponse`. Import from `fastapi.responses`.

**76. How do you return a streaming response (e.g., for large files or SSE)?**
```python
from fastapi.responses import StreamingResponse
import io

@app.get("/download/")
def download():
    def generate():
        for chunk in large_data:
            yield chunk
    return StreamingResponse(generate(), media_type="application/octet-stream")
```

**77. How do you return an HTML response?**
```python
from fastapi.responses import HTMLResponse

@app.get("/page", response_class=HTMLResponse)
def page():
    return "<html><body><h1>Hello</h1></body></html>"
```

**78. How do you return a file for download?**
```python
from fastapi.responses import FileResponse

@app.get("/download/")
def download():
    return FileResponse("report.pdf", filename="report.pdf")
```

---

## 🏗️ Project Structure & Best Practices

**79. What is the recommended FastAPI project structure for a medium-sized app?**
```
app/
├── main.py           # FastAPI app instance
├── routers/
│   ├── items.py      # APIRouter for items
│   └── users.py      # APIRouter for users
├── models/
│   └── item.py       # SQLAlchemy models
├── schemas/
│   └── item.py       # Pydantic models
├── crud/
│   └── item.py       # Database operations
├── dependencies.py   # Shared dependencies (get_db, get_current_user)
└── database.py       # Engine, SessionLocal, Base
```

**80. What is the CRUD pattern in FastAPI?**
Separating database operations into a dedicated `crud` module: `create_item(db, item)`, `get_item(db, id)`, `get_items(db, skip, limit)`, `update_item(db, id, item)`, `delete_item(db, id)`. Views call CRUD functions, keeping them thin.

**81. What is the difference between Pydantic v1 and v2 in FastAPI?**
FastAPI ≥ 0.100 uses Pydantic v2 by default. v2 is ~5-50× faster (Rust core), uses `model_validate()` instead of `.from_orm()`, `model_dump()` instead of `.dict()`, and `@field_validator` instead of `@validator`.

**82. How do you handle environment variables in FastAPI?**
Use Pydantic's `BaseSettings`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

**83. How do you implement rate limiting in FastAPI?**
Use `slowapi` (a FastAPI-compatible rate limiter based on `limits`):
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request): ...
```

**84. How do you implement caching in FastAPI?**
Use `fastapi-cache2` with Redis or in-memory backends:
```python
from fastapi_cache.decorator import cache

@app.get("/items/")
@cache(expire=60)
async def list_items(): ...
```

---

## 🔌 Advanced Features

**85. What is Server-Sent Events (SSE) and how is it implemented in FastAPI?**
SSE streams data from server to client over a long-lived HTTP connection. Use `StreamingResponse` with `text/event-stream` media type and `yield f"data: {message}\n\n"` in the generator.

**86. How do you implement GraphQL with FastAPI?**
Use `strawberry-graphql` with FastAPI integration:
```python
import strawberry
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello"

schema = strawberry.Schema(Query)
app.include_router(GraphQLRouter(schema), prefix="/graphql")
```

**87. How do you mount a sub-application in FastAPI?**
```python
from fastapi import FastAPI

app = FastAPI()
v2_app = FastAPI()

app.mount("/v2", v2_app)
```
Useful for API versioning or mounting WSGI apps (e.g., Django Admin).

**88. What is `Annotated` (from `typing`) and how does it improve FastAPI code?**
`Annotated[T, metadata]` attaches validation metadata directly to type hints:
```python
from typing import Annotated
from fastapi import Query

def search(q: Annotated[str, Query(min_length=3)] = None): ...
```
This is the recommended modern FastAPI style — it keeps validation co-located with the type.

**89. How do you implement pagination with FastAPI and SQLAlchemy?**
```python
@app.get("/items/")
def list_items(skip: int = 0, limit: int = Query(default=10, le=100), db: Session = Depends(get_db)):
    total = db.query(Item).count()
    items = db.query(Item).offset(skip).limit(limit).all()
    return {"total": total, "items": items, "skip": skip, "limit": limit}
```

**90. How do you implement soft delete in FastAPI?**
Add a `deleted_at: datetime | None = None` field to the model. Filter it out in queries: `db.query(Item).filter(Item.deleted_at == None)`. A DELETE endpoint sets `deleted_at = datetime.utcnow()` instead of removing the row.

---

## 🚀 Deployment

**91. How do you deploy FastAPI with Docker?**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**92. How do you run FastAPI with Gunicorn in production?**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
This uses 4 Uvicorn workers managed by Gunicorn for process supervision and graceful restarts.

**93. What is `uvicorn.workers.UvicornWorker`?**
A Gunicorn worker class that runs each worker as a Uvicorn ASGI server. This gives Gunicorn's process management (restart on crash, graceful reload) combined with Uvicorn's ASGI performance.

**94. How do you configure logging in FastAPI?**
FastAPI uses Python's `logging` module. Configure it in `lifespan` or at module level. Uvicorn's access log can be disabled with `--no-access-log` and customized with `--log-config`.

**95. How do you handle database migrations in production for FastAPI?**
Run `alembic upgrade head` in the container entrypoint before starting the server — the same pattern as Django's `manage.py migrate`.

---

## 🔬 Comparison & Trade-offs

**96. When should you choose FastAPI over Django REST Framework?**
FastAPI: async-first, high performance, minimal boilerplate, automatic docs, Pydantic validation, greenfield APIs.
DRF: mature ecosystem, built-in admin, ORM, auth, permissions, session handling, large community, batteries-included.

**97. What are FastAPI's main limitations compared to Django?**
No built-in admin panel, no built-in ORM, no built-in migrations, no built-in authentication, smaller plugin ecosystem. FastAPI is a microframework — you compose these components yourself.

**98. How does FastAPI compare to Flask for async applications?**
FastAPI is ASGI-native with async support built in. Flask (pre-2.0) is WSGI-synchronous. Flask-async extensions exist but are bolted on. FastAPI has automatic validation and docs that Flask lacks by default.

**99. What is the relationship between FastAPI and Starlette?**
FastAPI is built on top of Starlette (ASGI framework). FastAPI adds: Pydantic validation, dependency injection, OpenAPI generation, and type-based routing on top of Starlette's request handling, middleware, WebSockets, and background tasks.

**100. What makes FastAPI suitable for ML model serving?**
- Async endpoints handle concurrent inference requests without blocking
- Pydantic validates input feature vectors automatically
- Lifespan events load ML models once at startup
- `BackgroundTasks` handles async logging/monitoring
- FastAPI's performance is competitive with dedicated ML serving frameworks for I/O-bound inference paths
- Auto-generated OpenAPI docs make ML APIs self-documenting
