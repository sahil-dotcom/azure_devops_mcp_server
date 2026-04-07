#!/usr/bin/env python3

"""
MCP server for Azure DevOps Git tools.

This script initializes and runs the MCP server for Azure DevOps Git tools,
loading configuration from environment variables and registering all Git-related
MCP tools with authentication.
"""

import asyncio
import sys

from azure_devops_mcp.auth.pat import PATAuth  # Import the PAT authentication class
from azure_devops_mcp.client import AzureDevOpsClient
from azure_devops_mcp.config import Settings
from azure_devops_mcp.tools import git
from mcp.server.fastmcp import FastMCP


async def main() -> int:
    """
    Initialize and run the MCP server.

    Loads settings, validates credentials, creates the authentication object and
    MCP server, registers all Git tools, and runs the server using stdio transport.

    Returns:
        int: Exit code (0 for success, 1 for configuration error).
    """
    # Load settings from .env or environment variables
    settings = Settings()

    # Validate credentials
    if not settings.org_url or not settings.pat:
        print(
            "Error: AZURE_DEVOPS_ORG_URL and AZURE_DEVOPS_PAT must be set.",
            file=sys.stderr,
        )
        return 1

    # Create the authentication object
    auth = PATAuth(settings.pat)  # Adjust if your PATAuth expects different arguments

    # Create the MCP server
    mcp = FastMCP("Azure DevOps Git Server")

    # Use the client as an async context manager
    async with AzureDevOpsClient(
        settings.org_url, auth, api_version=settings.api_version
    ) as client:
        # Register all Git tools
        git.register(mcp, client)

        # Run the server using stdio transport
        await mcp.run_stdio_async()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
