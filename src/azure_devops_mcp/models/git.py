"""
Pydantic models for Azure DevOps Git operations.

This module defines input schemas for Azure DevOps Git-related MCP tools.
Each class represents the expected input for a specific Git operation, such as listing
repositories, branches, commits, pull requests, and more.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseInput(BaseModel):
    """
    Base input model for all Git operation schemas.

    Configures whitespace stripping and forbids extra fields.
    """

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class ListRepositoriesInput(BaseInput):
    """
    Input model for listing Git repositories in a project.

    Attributes:
        project (str): Azure DevOps project name.
        limit (int): Maximum number of repositories to return (default: 20).
    """

    project: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)


class GetRepositoryInput(BaseInput):
    """
    Input model for retrieving a specific repository.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)


class ListBranchesInput(BaseInput):
    """
    Input model for listing branches in a repository.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        limit (int): Maximum number of branches to return (default: 20).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)


class GetFileContentInput(BaseInput):
    """
    Input model for retrieving file content from a repository.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        file_path (str): Path to the file in the repository.
        branch (str | None): Branch name (optional).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    branch: str | None = None


class ListCommitsInput(BaseInput):
    """
    Input model for listing commits in a repository.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        branch (str | None): Branch name (optional).
        author (str | None): Commit author (optional).
        from_date (datetime | None): Start date for filtering commits (optional).
        to_date (datetime | None): End date for filtering commits (optional).
        path (str | None): File path to filter commits (optional).
        limit (int): Maximum number of commits to return (default: 20).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    branch: str | None = None
    author: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    path: str | None = None
    limit: int = Field(20, ge=1, le=100)


class GetCommitInput(BaseInput):
    """
    Input model for retrieving a specific commit.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        commit_id (str): Commit ID.
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    commit_id: str = Field(..., min_length=1)


class ListPullRequestsInput(BaseInput):
    """
    Input model for listing pull requests in a repository.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        status (str | None): Pull request status (optional).
        creator (str | None): Creator of the pull request (optional).
        reviewer (str | None): Reviewer of the pull request (optional).
        limit (int): Maximum number of pull requests to return (default: 20).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    status: str | None = None
    creator: str | None = None
    reviewer: str | None = None
    limit: int = Field(20, ge=1, le=100)


class GetPullRequestInput(BaseInput):
    """
    Input model for retrieving a specific pull request.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        pull_request_id (int): Pull request ID.
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    pull_request_id: int = Field(..., gt=0)


class CreatePullRequestInput(BaseInput):
    """
    Input model for creating a pull request.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        source_branch (str): Source branch name.
        target_branch (str): Target branch name.
        title (str): Title of the pull request.
        description (str | None): Description of the pull request (optional).
        reviewers (list[str] | None): List of reviewers (optional).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    source_branch: str = Field(..., min_length=1)
    target_branch: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str | None = None
    reviewers: list[str] | None = None


class UpdatePullRequestInput(BaseInput):
    """
    Input model for updating a pull request.

    Attributes:
        project (str): Azure DevOps project name.
        repository_id (str): Repository ID.
        pull_request_id (int): Pull request ID.
        title (str | None): New title (optional).
        description (str | None): New description (optional).
        status (str | None): New status (optional).
        auto_complete (bool | None): Whether to enable auto-complete (optional).
    """

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    pull_request_id: int = Field(..., gt=0)
    title: str | None = None
    description: str | None = None
    status: str | None = None
    auto_complete: bool | None = None
