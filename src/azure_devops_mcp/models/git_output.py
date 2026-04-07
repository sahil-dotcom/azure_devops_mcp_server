"""
Output models for Azure DevOps Git operations.

This module defines structured response schemas returned by MCP tools for repositories,
commits, pull requests, file content, and error responses.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

# ------------------------
# Common / Enums
# ------------------------


class PullRequestStatus(str, Enum):
    """
    Status of a pull request.

    Values:
        ACTIVE: The pull request is active.
        COMPLETE: The pull request is completed.
        ABANDONED: The pull request is abandoned.
    """

    ACTIVE = "active"
    COMPLETE = "completed"
    ABANDONED = "abandoned"


class MergeStatus(str, Enum):
    """
    Merge result status of a pull request.

    Values:
        SUCCEEDED: Merge succeeded.
        CONFLICTED: Merge has conflicts.
        FAILURE: Merge failed.
        NOT_SET: Merge status not set.
    """

    SUCCEEDED = "succeeded"
    CONFLICTED = "conflicted"
    FAILURE = "failure"
    NOT_SET = "notSet"


# ------------------------
# Repository
# ------------------------


class Repository(BaseModel):
    """
    Represents a Git repository.

    Attributes:
        id (str): Repository ID.
        name (str): Repository name.
        url (str | None): Repository URL.
        default_branch (str | None): Default branch name.
    """

    id: str
    name: str
    url: str | None = None
    default_branch: str | None = None


class ListRepositoriesOutput(BaseModel):
    """
    Response model for listing repositories.

    Attributes:
        count (int): Number of repositories returned.
        repositories (list[Repository]): List of repositories.
    """

    count: int
    repositories: list[Repository]


# ------------------------
# Branch
# ------------------------


class Branch(BaseModel):
    """
    Represents a Git branch.

    Attributes:
        name (str): Branch name.
        object_id (str): Object ID of the branch.
    """

    name: str
    object_id: str


class ListBranchesOutput(BaseModel):
    """
    Response model for listing branches.

    Attributes:
        count (int): Number of branches returned.
        branches (list[Branch]): List of branches.
    """

    count: int
    branches: list[Branch]


# ------------------------
# Commit
# ------------------------


class CommitAuthor(BaseModel):
    """
    Represents commit author information.

    Attributes:
        name (str | None): Author's name.
        email (str | None): Author's email.
        date (datetime | None): Commit date.
    """

    name: str | None = None
    email: str | None = None
    date: datetime | None = None


class Commit(BaseModel):
    """
    Represents a Git commit.

    Attributes:
        commit_id (str): Commit ID.
        comment (str | None): Commit message/comment.
        author (CommitAuthor | None): Commit author information.
        url (str | None): Commit URL.
    """

    commit_id: str
    comment: str | None = None
    author: CommitAuthor | None = None
    url: str | None = None


class ListCommitsOutput(BaseModel):
    """
    Response model for listing commits.

    Attributes:
        count (int): Number of commits returned.
        commits (list[Commit]): List of commits.
    """

    count: int
    commits: list[Commit]


# ------------------------
# Pull Request
# ------------------------


class Reviewer(BaseModel):
    """
    Represents a pull request reviewer.

    Attributes:
        display_name (str | None): Reviewer's display name.
        unique_name (str | None): Reviewer's unique name.
        vote (int | None): Reviewer's vote (Azure uses int votes).
    """

    display_name: str | None = None
    unique_name: str | None = None
    vote: int | None = None  # Azure uses int votes


class PullRequest(BaseModel):
    """
    Represents a pull request.

    Attributes:
        id (int): Pull request ID.
        title (str): Pull request title.
        status (PullRequestStatus): Status of the pull request.
        merge_status (MergeStatus | None): Merge status.
        source_branch (str | None): Source branch name.
        target_branch (str | None): Target branch name.
        created_by (str | None): Creator of the pull request.
        reviewers (list[Reviewer] | None): List of reviewers.
        creation_date (datetime | None): Creation date.
    """

    id: int
    title: str
    status: PullRequestStatus
    merge_status: MergeStatus | None = None

    source_branch: str | None = None
    target_branch: str | None = None

    created_by: str | None = None
    reviewers: list[Reviewer] | None = None

    creation_date: datetime | None = None


class ListPullRequestsOutput(BaseModel):
    """
    Response model for listing pull requests.

    Attributes:
        count (int): Number of pull requests returned.
        pull_requests (list[PullRequest]): List of pull requests.
    """

    count: int
    pull_requests: list[PullRequest]


# ------------------------
# File Content
# ------------------------


class FileContent(BaseModel):
    """
    Represents file content retrieved from a repository.

    Attributes:
        path (str): File path.
        content (str): File content.
        size (int | None): File size in bytes (optional).
        encoding (str | None): File encoding (optional).
    """

    path: str
    content: str
    size: int | None = None
    encoding: str | None = None


# ------------------------
# Error (optional but recommended)
# ------------------------


class ErrorResponse(BaseModel):
    """
    Standard error response for MCP tools.

    Attributes:
        error (str): Error message.
    """

    error: str
