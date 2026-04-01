'''Error handling helpers for Azure Devops API responses.'''

import logging
import httpx

logger = logging.getLogger(__name__)

_STATUS_MESSAGES: dict[int, str] = {
    400: "Bad Request - The request was invalid or cannot be served.",
    401: "Authentication failed - check your credentials.",
    403: (
        "Permission denied - you do not have access to this resource. "
    ),
    404: "Resource not found - Verify the ID or name is correct.",
    409: "Conflict - The resource may have been modified.",
    429: "Rate limit exceeded - Too many requests. Please retry later.",
}

def handle_api_error(e: Exception) -> str:
    """Return a user-friendly message for a failed API call."""
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        if status in _STATUS_MESSAGES:
            return _STATUS_MESSAGES[status]
        if 500 <= status < 600:
            return (
                f"Azure Devops server error ({status}). "
                "Please try again later."
            )
        return f"API request failed with status {status}."
    
    if isinstance(e, httpx.TimeoutException):
        return (
            "Request timed out - The server may be "
            "under heavy load - please try again later."
        )

    if isinstance(e, httpx.RequestError):
        return f"Network error while connecting to Azure DevOps: {e}"

    logger.exception("Unexpected error in Azure DevOps API call")
    return "An unexpected error occurred while processing the request."