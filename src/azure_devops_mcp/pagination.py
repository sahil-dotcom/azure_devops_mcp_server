"""Pagination helper for Azure DevOps list endpoints."""

from azure_devops_mcp.client import AzureDevOpsClient

async def paginate(
    client: AzureDevOpsClient,
    path: str,
    project: str | None = None,
    params: dict | None = None,
    limit: int = 100,
) -> list[dict]:
    """Fetch all pages and return up to `limit` items."""
    items: list[dict] = []
    params = dict(params) if params else {}

    while True:
        response = await client.request_raw(
            "GET", path, project=project, params=params
        )
        data = response.json()

        for item in data.get("value", []):
            items.append(item)
            if len(items) >= limit:
                return items

        contiuation = response.headers.get("x-ms-continuationtoken")
        if not contiuation:
            break
        params["continuationToken"] = contiuation
    return items