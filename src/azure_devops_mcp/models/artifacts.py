"""
Pydantic models for Azure DevOps Artifacts tools input schemas.

This module defines input schemas for Azure DevOps Artifacts-related MCP tools.
Each class represents the expected input for a specific Artifacts operation,
such as listing feeds, retrieving a feed, listing packages,
and getting package versions.
"""

from pydantic import BaseModel, ConfigDict, Field


class ListFeedsInput(BaseModel):
    """
    Input model for listing feeds.

    Attributes:
        limit (int): Maximum number of feeds to return (default: 20).
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    limit: int = Field(default=20, ge=1, le=100)


class GetFeedInput(BaseModel):
    """
    Input model for retrieving a feed.

    Attributes:
        feed_id (str): Feed name.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    feed_id: str = Field(..., min_length=1, description="Feed name")


class ListPackagesInput(BaseModel):
    """
    Input model for listing packages in a feed.

    Attributes:
        feed_id (str): Feed name.
        limit (int): Maximum number of packages to return (default: 20).
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    feed_id: str = Field(..., min_length=1, description="Feed name")
    limit: int = Field(default=20, ge=1, le=100)


class GetPackageVersionInput(BaseModel):
    """
    Input model for retrieving a package version.

    Attributes:
        feed_id (str): Feed name.
        package_id (str): Package name.
        limit (int): Maximum number of versions to return (default: 20).
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    feed_id: str = Field(..., min_length=1)
    package_id: str = Field(..., min_length=1)
    limit: int = Field(default=20, ge=1, le=100)
