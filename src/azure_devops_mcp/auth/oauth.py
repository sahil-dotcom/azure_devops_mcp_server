'''
OAuth client-credentials authentication for Azure DevOps
'''
import time
import httpx

_TOKEN_REFRESH_MARGIN = 300

class OAuthAuth:
    """Acquire and cache OAuth tokens via client credentials flow."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._token: str | None = None
        self._token_expiry: float = 0.0

    async def get_headers(self) -> dict[str, str]:
        """Return Authorization headers, refreshing the token if needed."""
        token_expired = (
            time.time() >= self._token_expiry - _TOKEN_REFRESH_MARGIN
        )
        if self._token is None or token_expired:
            await self._acquire_token()
        return {"Authorization": f"Bearer {self._token}"}
    
    async def _acquire_token(self) -> None:
        """Acquire a new OAuth token."""
        url = (
            "https://login.microsoftonline.com/"
            f"{self.tenant_id}/oauth2/v2.0/token"
        )
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "499b84ac-1321-427f-aa17-267ca6975798/.default",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            response.raise_for_status()
            token_data = response.json()

        self._token = token_data["access_token"]
        self._token_expiry = time.time() + token_data["expires_in"]
