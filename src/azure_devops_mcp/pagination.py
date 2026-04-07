"""
Pagination helper for Azure DevOps list endpoints.

This module provides a helper function to fetch all pages of results from
Azure DevOps list endpoints,
respecting continuation tokens and a configurable item limit.
"""

from azure_devops_mcp.client import AzureDevOpsClient


async def paginate(
    client: AzureDevOpsClient,
    path: str,
    project: str | None = None,
    params: dict | None = None,
    limit: int = 100,
) -> list[dict]:
    """
    Fetch all pages and return up to `limit` items from a paginated
    Azure DevOps endpoint.

    Args:
        client (AzureDevOpsClient): The Azure DevOps client instance.
        path (str): The API path to fetch.
        project (str, optional): Project name. Defaults to None.
        params (dict, optional): Query parameters. Defaults to None.
        limit (int, optional): Maximum number of items to return. Defaults to 100.

    Returns:
        list[dict]: List of items up to the specified limit.
    """
    items: list[dict] = []
    params = dict(params) if params else {}

    while True:
        response = await client.request_raw("GET", path, project=project, params=params)
        data = response.json()

        for item in data.get("value", []):
            items.append(item)
            if len(items) >= limit:
                return items

        continuation = response.headers.get("x-ms-continuationtoken")
        if not continuation:
            break
        params["continuationToken"] = continuation
    return items
