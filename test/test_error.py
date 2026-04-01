import httpx
from azure_devops_mcp.shared.error import handle_api_error

def _make_status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://dev.azure.com/testorg/_apis/projects")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(
        message=f"HTTP {status_code}",
        request=request,
        response=response,
    )

class TestHandleApiError:
    def test_401_returns_auth_failed(self):
        msg = handle_api_error(_make_status_error(401))
        assert "Authentication failed" in msg
        assert "PAT" in msg or "credentials" in msg.lower()

    def test_403_returns_permission_denied(self):
        msg = handle_api_error(_make_status_error(403))
        assert "Permission denied" in msg or "permission" in msg.lower()

    def test_404_returns_not_found(self):
        msg = handle_api_error(_make_status_error(404))
        assert "Resource not found" in msg or "not found" in msg.lower()

    def test_429_returns_rate_limit(self):
        msg = handle_api_error(_make_status_error(429))
        assert "Rate limit exceeded" in msg or "rate limit" in msg.lower()
    
    def test_timeout_exception(self):
        err = httpx.ReadTimeout("Connection timed out")
        msg = handle_api_error(err)
        assert "request timed out" in msg.lower()

    def test_generic_exception_safe_message(self):
        err = RuntimeError("some internal detail /secret/path/key=abc123")
        msg = handle_api_error(err)
        assert "An unexpected error occurred" in msg or "unexpected" in msg.lower()
        assert "/secret/path" not in msg
        assert "abc123" not in msg