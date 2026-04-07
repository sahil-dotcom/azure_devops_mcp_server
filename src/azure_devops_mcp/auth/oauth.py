"""
OAuth client-credentials authentication for Azure DevOps.

This module provides the OAuthAuth class, which implements the client credentials flow
for acquiring and caching OAuth tokens for Azure DevOps REST API access.

Example:
    auth = OAuthAuth(client_id, client_secret, tenant_id)
    headers = await auth.get_headers()
"""

import time

import httpx

_TOKEN_REFRESH_MARGIN = 300


class OAuthAuth:
    """
    Implements OAuth 2.0 client credentials flow for Azure DevOps.

    This class acquires and caches OAuth tokens using the provided Azure AD
    application credentials. It automatically refreshes tokens before expiry
    and provides authorization headers for API requests.

    Attributes:
        client_id (str): Azure AD application (client) ID.
        client_secret (str): Azure AD application client secret.
        tenant_id (str): Azure AD tenant ID.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ) -> None:
        """Initializes the OAuthAuth instance.

        Args:
            client_id (str): The Azure AD application (client) ID.
            client_secret (str): The Azure AD application client secret.
            tenant_id (str): The Azure AD tenant ID.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._token: str | None = None
        self._token_expiry: float = 0.0

    async def get_headers(self) -> dict[str, str]:
        """Get the authorization headers with a valid OAuth token.

        Returns:
            dict[str, str]: A dictionary containing the Authorization header.

        Raises:
            httpx.HTTPStatusError: If token acquisition fails.
        """
        token_expired = time.time() >= self._token_expiry - _TOKEN_REFRESH_MARGIN
        if self._token is None or token_expired:
            await self._acquire_token()
        return {"Authorization": f"Bearer {self._token}"}

    async def _acquire_token(self) -> None:
        """Acquire a new OAuth token using the client credentials flow.

        This method updates the cached token and its expiry time.

        Raises:
            httpx.HTTPStatusError: If the token request fails.
        """
        url = "https://login.microsoftonline.com/" f"{self.tenant_id}/oauth2/v2.0/token"
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
