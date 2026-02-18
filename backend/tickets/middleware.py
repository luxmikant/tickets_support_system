"""
Custom middleware for the Support Ticket System.

RequestLoggingMiddleware — logs every request with method, path, status, duration.
ExceptionHandlingMiddleware — catches unhandled exceptions, returns structured JSON.
"""

import json
import logging
import time
import traceback

from django.http import JsonResponse

logger = logging.getLogger('tickets')


class RequestLoggingMiddleware:
    """
    Logs HTTP requests with method, path, status code, and response time.

    Log levels:
        INFO  — 2xx responses
        WARNING — 4xx responses
        ERROR — 5xx responses
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        duration_ms = (time.monotonic() - start_time) * 1000
        status_code = response.status_code
        method = request.method
        path = request.get_full_path()

        log_message = f'{method} {path} → {status_code} ({duration_ms:.1f}ms)'

        if 500 <= status_code < 600:
            logger.error(log_message)
        elif 400 <= status_code < 500:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response


class ExceptionHandlingMiddleware:
    """
    Catches unhandled exceptions that escape the view layer and returns
    a structured JSON error response instead of raw HTML tracebacks.

    In DEBUG mode, the traceback is included in the response.
    In production, only a generic message is returned (traceback still logged).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        tb = traceback.format_exc()
        logger.error(
            f'Unhandled exception on {request.method} {request.get_full_path()}: '
            f'{exception.__class__.__name__}: {exception}\n{tb}'
        )

        from django.conf import settings

        response_data = {
            'error': 'Internal server error',
            'detail': str(exception) if settings.DEBUG else 'An unexpected error occurred.',
        }

        return JsonResponse(response_data, status=500)
