"""
Gunicorn configuration for production deployment.

Features:
    - gthread workers for I/O-bound operations (LLM API calls)
    - Graceful shutdown with 30s timeout
    - Worker recycling to prevent memory leaks
    - Lifecycle logging hooks
"""

import multiprocessing
import os

# =============================================================================
# SERVER SOCKET
# =============================================================================

bind = '0.0.0.0:8000'
backlog = 2048

# =============================================================================
# WORKERS
# =============================================================================

workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gthread'    # Thread-based workers — ideal for I/O (LLM API calls)
threads = 4                 # Threads per worker
worker_connections = 1000

# =============================================================================
# TIMEOUTS & GRACEFUL SHUTDOWN
# =============================================================================

timeout = 120               # Max time (seconds) for a request to complete
graceful_timeout = 30       # Time workers get to finish in-flight requests on SIGTERM
keepalive = 5               # Keep-alive connections timeout

# =============================================================================
# WORKER RECYCLING (prevents memory leaks over long uptime)
# =============================================================================

max_requests = 1000         # Restart worker after N requests
max_requests_jitter = 50    # Randomize restart to avoid thundering herd

# =============================================================================
# APP LOADING
# =============================================================================

preload_app = True           # Load Django before forking workers (shared memory)

# =============================================================================
# LOGGING
# =============================================================================

accesslog = '-'              # Log to stdout
errorlog = '-'               # Log to stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# =============================================================================
# LIFECYCLE HOOKS — log server events for observability
# =============================================================================


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info('Gunicorn master starting — PID %s', server.pid)


def on_reload(server):
    """Called to recycle workers during a reload."""
    server.log.info('Gunicorn master reloading')


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info('Worker spawned — PID %s', worker.pid)


def worker_exit(server, worker):
    """Called when a worker exits — cleanup happens here."""
    server.log.info('Worker exiting — PID %s', worker.pid)


def on_exit(server):
    """Called just before exiting Gunicorn master."""
    server.log.info('Gunicorn master shutting down gracefully')
