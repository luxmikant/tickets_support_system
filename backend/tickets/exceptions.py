"""
Custom DRF exception handler.

Wraps all API errors in a consistent envelope:
    {"error": "...", "details": {...}}
"""

import logging

from rest_framework.views import exception_handler

logger = logging.getLogger('tickets')


def custom_exception_handler(exc, context):
    """
    Extends DRF's default exception handler to return errors
    in a consistent JSON envelope format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Build a consistent error envelope
        error_data = {
            'error': _get_error_title(response.status_code),
            'details': response.data,
        }
        response.data = error_data

        # Log 5xx errors
        if response.status_code >= 500:
            view = context.get('view', None)
            logger.error(
                f'DRF exception in {view.__class__.__name__ if view else "unknown"}: '
                f'{exc.__class__.__name__}: {exc}'
            )

    return response


def _get_error_title(status_code: int) -> str:
    """Map HTTP status codes to human-readable error titles."""
    titles = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        409: 'Conflict',
        429: 'Too Many Requests',
        500: 'Internal Server Error',
    }
    return titles.get(status_code, f'Error {status_code}')
