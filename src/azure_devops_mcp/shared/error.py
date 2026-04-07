"""
Error handling helpers for Azure DevOps API responses.

This module provides utilities for logging and returning user-friendly error messages
from Azure DevOps API exceptions.
"""

import logging

import httpx

logger = logging.getLogger(__name__)

_STATUS_MESSAGES: dict[int, str] = {
    400: "Bad Request - The request was invalid or cannot be served.",
    401: "Authentication failed - check your credentials.",
    403: ("Permission denied - you do not have access to this resource. "),
    404: "Resource not found - Verify the ID or name is correct.",
    409: "Conflict - The resource may have been modified.",
    429: "Rate limit exceeded - Too many requests. Please retry later.",
}


def handle_api_error(e: Exception) -> str:
    """
    Return a user-friendly message for a failed API call.

    Args:
        e (Exception): The exception raised during the API call.

    Returns:
        str: A user-friendly error message describing the failure.
    """
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        msg = _STATUS_MESSAGES.get(status, f"API request failed with status {status}.")
        logger.error("HTTP %d: %s", status, e.response.text[:200])  # lazy % formatting
        return msg
    if isinstance(e, httpx.TimeoutException):
        logger.warning("Request timed out")
        return "Request timed out - please retry."
    if isinstance(e, httpx.RequestError):
        logger.error("Network error: %s", e)
        return f"Network error: {e}"
    logger.exception("Unexpected error")
    return "An unexpected error occurred."
