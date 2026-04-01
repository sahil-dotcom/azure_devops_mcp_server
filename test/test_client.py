import httpx
import pytest
import respx
from azure_devops_mcp.auth import PATAuth
from azure_devops_mcp.client import AzureDevOpsClient

@pytest.fixture 
def auth():
    return PATAuth("test-pat")

@pytest.fixture
def client(auth):
    return AzureDevOpsClient(
        org_url="https://dev.azure.com/testorg", 
        auth=auth,
        api_version="7.1",
    )

class TestAzureDevOpsClient:
    @pytest.mark.asyncio
    @respx.mock
    async def test_request_constructs_org_level_url(self, client, auth):
        route = respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).respond(json={"value": [], "count": 0})

        async with client:
            result = await client._request("GET", "projects")
        
        assert route.called
        assert result == {"value": [], "count": 0}

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_constructs_project_level_url(self, client):
        route = respx.get(
            "https://dev.azure.com/testorg/MyProject/_apis/wit/workitems",
            params={"api-version": "7.1"},
        ).respond(json={"value": [], "count": 0})

        async with client:
            result = await client.request("GET", "wit/workitems", project="MyProject")
        
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_includes_auth_headers(self, client, auth):
        expected_headers = None

        def check_request(request):
            nonlocal expected_headers
            expected_headers = request.headers.get("Authorization")
            return httpx.Response(200, json={"value": []})
        
        respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).mock(side_effect=check_request)

        async with client:
            await client.request("GET", "projects")

        auth_headers = await auth.get_headers()
        assert expected_headers == auth_headers.get("Authorization")

    @pytest.mark.asyncio
    @respx.mock
    async def test_retries_on_429(self, client):
        route = respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).mock(
            side_effect=[
                httpx.Response(429, json={"message": "Rate limited"}),
                httpx.Response(200, json={"value": []}),
            ]
        )
        async with client:
            result = await client.request("GET", "projects")
        
        assert route.call_count == 2
        assert result == {"value": []}

    @pytest.mark.asyncio
    @respx.mock
    async def test_retries_on_5xx(self, client):
        route = respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).mock(
            side_effect=[
                httpx.Response(503, json={"message": "Server unavailable"}),
                httpx.Response(200, json={"value": []}),
            ]
        )

        async with client:
            result = await client.request("GET", "projects")
        
        assert route.call_count == 2
        assert result == {"value": []}

    @pytest.mark.asyncio
    @respx.mock
    async def test_raises_after_max_retries(self, client):
        respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).mock(
            side_effect=[
                httpx.Response(503, json={"message": "Server unavailable"}),
                httpx.Response(503, json={"message": "Server unavailable"}),
                httpx.Response(503, json={"message": "Server unavailable"}),
            ]
        )

        async with client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.request("GET", "projects")

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_timeout(self, client):
        respx.get(
            "https://dev.azure.com/testorg/_apis/projects",
            params={"api-version": "7.1"},
        ).mock(side_effect=httpx.ReadTimeout("Request timed out"))

        async with client:
            with pytest.raises(httpx.ReadTimeout):
                await client.request("GET", "projects")