"""
MCP tools for Azure DevOps artifacts feeds and packages.

This module registers and implements MCP tools for interacting with+
Azure DevOps Artifacts, including listing feeds, retrieving feed details,
listing packages, and getting package versions.
"""

import json

import httpx

from azure_devops_mcp.client import AzureDevOpsClient
from azure_devops_mcp.models.artifacts import (
    GetFeedInput,
    GetPackageVersionInput,
    ListFeedsInput,
    ListPackagesInput,
)
from azure_devops_mcp.shared.error import handle_api_error

_state: dict[str, AzureDevOpsClient] = {}


def register(mcp, client: AzureDevOpsClient) -> None:
    """
    Register artifact tools with the MCP server.

    Args:
        mcp: The MCP server instance.
        client (AzureDevOpsClient): The Azure DevOps client to use for API calls.
    """
    _state["client"] = client

    mcp.tool(
        name="azuredevops_list_feeds",
        description="List all artifact feeds in the organization",
    )(azuredevops_list_feeds)

    mcp.tool(
        name="azuredevops_get_feed",
        description="Get a specific artifact feed by name or ID",
    )(azuredevops_get_feed)

    mcp.tool(
        name="azuredevops_list_packages",
        description="List all packages in a specific feed",
    )(azuredevops_list_packages)

    mcp.tool(
        name="azuredevops_get_package_version",
        description="Get a specific package version by name or ID",
    )(azuredevops_get_package_version)


async def azuredevops_list_feeds(limit: int = 20) -> str:
    """
    List all artifact feeds in the organization.

    Args:
        limit (int, optional): Maximum number of feeds to return. Defaults to 20.

    Returns:
        str: JSON string containing the list of feeds or an error message.
    """
    inp = ListFeedsInput(limit=limit)
    try:
        data = await _state["client"].get(
            "package/feeds",
            params={"$top": inp.limit},
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)


async def azuredevops_get_feed(feed_id: str) -> str:
    """
    Get details of a specific feed.

    Args:
        feed_id (str): The feed name or ID.

    Returns:
        str: JSON string containing the feed details or an error message.
    """
    inp = GetFeedInput(feed_id=feed_id)
    try:
        data = await _state["client"].get(
            f"package/feeds/{inp.feed_id}",
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)


async def azuredevops_list_packages(feed_id: str, limit: int = 20) -> str:
    """
    List all packages in a specific feed.

    Args:
        feed_id (str): The feed name or ID.
        limit (int, optional): Maximum number of packages to return. Defaults to 20.

    Returns:
        str: JSON string containing the list of packages or an error message.
    """
    inp = ListPackagesInput(feed_id=feed_id, limit=limit)
    try:
        data = await _state["client"].get(
            f"package/feeds/{inp.feed_id}/packages",
            params={"$top": inp.limit},
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)


async def azuredevops_get_package_version(
    feed_id: str, package_id: str, limit: int = 20
) -> str:
    """
    Get a specific package version by name or ID.

    Args:
        feed_id (str): The feed name or ID.
        package_id (str): The package name or ID.
        limit (int, optional): Maximum number of versions to return. Defaults to 20.

    Returns:
        str: JSON string containing the package version details or an error message.
    """
    inp = GetPackageVersionInput(feed_id=feed_id, package_id=package_id, limit=limit)
    try:
        data = await _state["client"].get(
            f"package/feeds/{inp.feed_id}/packages/{inp.package_id}/versions",
            params={"$top": inp.limit},
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
