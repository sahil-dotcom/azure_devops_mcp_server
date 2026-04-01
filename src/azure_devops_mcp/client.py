"""Async HTTP client for Azure DevOps REST API with retry logic and authentication."""
import asyncio
import logging
import httpx
from azure_devops_mcp.auth import AuthProvider

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_FACTOR = [1, 2, 4]
_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

class AzureDevOpsClient:
    """Async client wrapping Azure DevOps REST API with retry logic and authentication."""

    def __init__(
        self,
        org_url: str,
        auth: AuthProvider,
        api_version: str = "7.1",
        timeout: float = 30.0,
    ) -> None:
        self._org_url = org_url.rstrip("/")  # FIX 1: was `self.org_url`
        self.auth = auth
        self.api_version = api_version
        self._http: httpx.AsyncClient | None = None
        self.timeout = timeout

    async def __aenter__(self) -> "AzureDevOpsClient":
        self._http = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    def _build_url(self, path: str, project: str | None = None) -> str:
        if project:
            return f"{self._org_url}/{project}/_apis/{path}"
        return f"{self._org_url}/_apis/{path}"

    async def _request(
        self,
        method: str,
        path: str,
        project: str | None = None,
        params: dict | None = None,
        json: dict | None = None,
        content_type: str | None = None,
        extra_headers: dict | None = None,
    ) -> dict:
        """Send an API request and return the parsed JSON response."""
        if self._http is None:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context.")
        
        url = self._build_url(path, project)
        params = dict(params) if params else {}
        params["api-version"] = self.api_version

        headers = await self.auth.get_headers()  # FIX 2: was `self._auth`
        if content_type:
            headers["Content-Type"] = content_type
        if extra_headers:
            headers.update(extra_headers)

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            response = await self._http.request(
                method, url, params=params, json=json, headers=headers
            )

            if response.status_code not in _RETRY_STATUS_CODES:
                response.raise_for_status()
                return response.json()

            last_exc = httpx.HTTPStatusError(
                message=f"HTTP {response.status_code}",
                request=response.request,
                response=response,
            )

            if attempt < _MAX_RETRIES - 1:
                delay = _BACKOFF_FACTOR[attempt]
                logger.warning(
                    "Request to %s returned %s, retrying in %ss (attempt %d/%d)",
                    url, response.status_code, delay, attempt + 1, _MAX_RETRIES,
                )
                await asyncio.sleep(delay)
        raise last_exc

    async def request(
        self,
        method: str,
        path: str,
        project: str | None = None,
        params: dict | None = None,
        json: dict | None = None,
        content_type: str | None = None,
        extra_headers: dict | None = None,
    ) -> dict:
        """Public alias for _request."""
        return await self._request(
            method, path,
            project=project,
            params=params,
            json=json,
            content_type=content_type,
            extra_headers=extra_headers,
        )

    async def request_raw(
        self,
        method: str,
        path: str,
        project: str | None = None,
        params: dict | None = None,
        json: dict | None = None,
    ) -> httpx.Response:
        """Like request(), but return the raw httpx.Response (for header access)."""
        if self._http is None:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context.")
        
        url = self._build_url(path, project)
        params = dict(params) if params else {}
        params["api-version"] = self.api_version

        headers = await self.auth.get_headers()  # FIX 2: was `self._auth`

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            response = await self._http.request(
                method, url, params=params, json=json, headers=headers
            )

            if response.status_code not in _RETRY_STATUS_CODES:
                response.raise_for_status()
                return response

            last_exc = httpx.HTTPStatusError(
                message=f"HTTP {response.status_code}",
                request=response.request,
                response=response,
            )

            if attempt < _MAX_RETRIES - 1:
                delay = _BACKOFF_FACTOR[attempt]
                logger.warning(
                    "Request to %s returned %s, retrying in %ss (attempt %d/%d)",
                    url, response.status_code, delay, attempt + 1, _MAX_RETRIES,
                )
                await asyncio.sleep(delay)
        raise last_exc

    async def get(self, path: str, **kwargs) -> dict:
        """Send a GET request and return the parsed JSON response."""
        return await self._request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> dict:
        """Send a POST request and return the parsed JSON response."""
        return await self._request("POST", path, **kwargs)

    async def patch(self, path: str, **kwargs) -> dict:
        """Send a PATCH request and return the parsed JSON response."""
        return await self._request("PATCH", path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> dict:
        """Send a DELETE request and return the parsed JSON response."""
        return await self._request("DELETE", path, **kwargs)