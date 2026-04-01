import base64
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure_devops_mcp.auth import AuthProvider
from azure_devops_mcp.auth.oauth import OAuthAuth
from azure_devops_mcp.auth.pat import PATAuth

class TestPATAuth:
    @pytest.mark.asyncio
    async def test_get_headers_returns_basic_auth(self):
        auth = PATAuth("my-test-pat")
        headers = await auth.get_headers()

        expected_b64 = base64.b64encode(b":my-test-pat").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_b64}"}

    @pytest.mark.asyncio
    async def test_implements_auth_provider(self):
        auth = PATAuth("my-test-pat")
        assert isinstance(auth, AuthProvider)

class TestOAuthAuth:
    @pytest.mark.asyncio
    async def test_get_headers_returns_bearer_token(self):
        auth = OAuthAuth(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("azure_devops_mcp.auth.oauth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            headers = await auth.get_headers()
        assert headers == {"Authorization": "Bearer test-access-token"}

    @pytest.mark.asyncio
    async def test_refreshes_expired_token(self):
        auth = OAuthAuth(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )
        auth._token = "old-token"
        auth._token_expiry = time.time() - 10

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("azure_devops_mcp.auth.oauth.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client_cls.return_value = mock_client

            headers = await auth.get_headers()
        assert headers == {"Authorization": "Bearer new-access-token"}

    @pytest.mark.asyncio
    async def test_uses_cached_token_when_not_expired(self):
        auth = OAuthAuth(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        auth._token = "cached-token"
        auth._token_expiry = time.time() + 3600

        headers = await auth.get_headers()
        assert headers == {"Authorization": "Bearer cached-token"}

    @pytest.mark.asyncio
    async def test_implements_auth_provider(self):
        auth = OAuthAuth(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )
        assert isinstance(auth, AuthProvider)