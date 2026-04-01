"""Tests for Git models (models/git.py) and Git tools (tools/git.py)."""

import json
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from azure_devops_mcp.models.git import (
    listRepositoriesInput,
    getRepositoryInput,
    listBranchesInput,
    getFileContentInput,
    ListCommitsInput,
    GetCommitInput,
    ListPullRequestsInput,
    GetPullRequestInput,
    CreatePullRequestInput,
    UpdatePullRequestInput,
)
import azure_devops_mcp.tools.git as git_tools


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client() -> MagicMock:
    client = MagicMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.patch = AsyncMock()
    client.request_raw = AsyncMock()
    return client


def _make_status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://dev.azure.com/test/_apis/")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(
        message=f"HTTP {status_code}", request=request, response=response
    )


# ===========================================================================
# MODEL TESTS — models/git.py
# ===========================================================================


class TestListRepositoriesInput:
    def test_valid_minimal(self):
        m = listRepositoriesInput(project="myproject")
        assert m.project == "myproject"
        assert m.limit == 20

    def test_custom_limit(self):
        m = listRepositoriesInput(project="myproject", limit=50)
        assert m.limit == 50

    def test_limit_min_boundary(self):
        m = listRepositoriesInput(project="p", limit=1)
        assert m.limit == 1

    def test_limit_max_boundary(self):
        m = listRepositoriesInput(project="p", limit=100)
        assert m.limit == 100

    def test_limit_below_min_raises(self):
        with pytest.raises(ValidationError):
            listRepositoriesInput(project="p", limit=0)

    def test_limit_above_max_raises(self):
        with pytest.raises(ValidationError):
            listRepositoriesInput(project="p", limit=101)

    def test_empty_project_raises(self):
        with pytest.raises(ValidationError):
            listRepositoriesInput(project="")

    def test_extra_field_raises(self):
        with pytest.raises(ValidationError):
            listRepositoriesInput(project="p", unknown_field="x")


class TestGetRepositoryInput:
    def test_valid(self):
        m = getRepositoryInput(project="proj", repository_id="repo-123")
        assert m.repository_id == "repo-123"

    def test_empty_repository_id_raises(self):
        with pytest.raises(ValidationError):
            getRepositoryInput(project="proj", repository_id="")

    def test_missing_repository_id_raises(self):
        with pytest.raises(ValidationError):
            getRepositoryInput(project="proj")


class TestListBranchesInput:
    def test_valid_defaults(self):
        m = listBranchesInput(project="proj", repository_id="repo")
        assert m.limit == 20

    def test_valid_custom_limit(self):
        m = listBranchesInput(project="proj", repository_id="repo", limit=5)
        assert m.limit == 5

    def test_limit_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            listBranchesInput(project="proj", repository_id="repo", limit=200)


class TestGetFileContentInput:
    def test_valid_no_branch(self):
        m = getFileContentInput(project="p", repository_id="r", file_path="/src/main.py")
        assert m.branch is None

    def test_valid_with_branch(self):
        m = getFileContentInput(project="p", repository_id="r", file_path="/README.md", branch="main")
        assert m.branch == "main"

    def test_empty_file_path_raises(self):
        with pytest.raises(ValidationError):
            getFileContentInput(project="p", repository_id="r", file_path="")


class TestListCommitsInput:
    def test_valid_minimal(self):
        m = ListCommitsInput(project="p", repository_id="r")
        assert m.branch is None
        assert m.author is None
        assert m.from_data is None
        assert m.to_date is None
        assert m.path is None
        assert m.limit == 20

    def test_all_optional_fields(self):
        m = ListCommitsInput(
            project="p",
            repository_id="r",
            branch="main",
            author="sahil",
            from_data="2024-01-01",
            to_date="2024-12-31",
            path="/src",
            limit=10,
        )
        assert m.branch == "main"
        assert m.author == "sahil"
        assert m.from_data == "2024-01-01"

    def test_limit_bounds(self):
        with pytest.raises(ValidationError):
            ListCommitsInput(project="p", repository_id="r", limit=0)


class TestGetCommitInput:
    def test_valid(self):
        m = GetCommitInput(project="p", repository_id="r", commit_id="abc123")
        assert m.commit_id == "abc123"

    def test_empty_commit_id_raises(self):
        with pytest.raises(ValidationError):
            GetCommitInput(project="p", repository_id="r", commit_id="")


class TestListPullRequestsInput:
    def test_valid_defaults(self):
        m = ListPullRequestsInput(project="p", repository_id="r")
        assert m.status is None
        assert m.creator is None
        assert m.reviewer is None
        assert m.limit == 20

    def test_with_filters(self):
        m = ListPullRequestsInput(
            project="p", repository_id="r",
            status="active", creator="alice", reviewer="bob", limit=5
        )
        assert m.status == "active"
        assert m.creator == "alice"
        assert m.reviewer == "bob"


class TestGetPullRequestInput:
    def test_valid(self):
        m = GetPullRequestInput(project="p", repository_id="r", pull_request_id=42)
        assert m.pull_request_id == 42

    def test_zero_pr_id_raises(self):
        with pytest.raises(ValidationError):
            GetPullRequestInput(project="p", repository_id="r", pull_request_id=0)

    def test_negative_pr_id_raises(self):
        with pytest.raises(ValidationError):
            GetPullRequestInput(project="p", repository_id="r", pull_request_id=-1)


class TestCreatePullRequestInput:
    def test_valid_minimal(self):
        m = CreatePullRequestInput(
            project="p", repository_id="r",
            source_branch="feature/x", target_branch="main", title="My PR"
        )
        assert m.description is None
        assert m.reviewer is None

    def test_with_reviewers(self):
        m = CreatePullRequestInput(
            project="p", repository_id="r",
            source_branch="feat", target_branch="main",
            title="PR", reviewer=["alice", "bob"]
        )
        assert len(m.reviewer) == 2

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            CreatePullRequestInput(
                project="p", repository_id="r",
                source_branch="feat", target_branch="main", title=""
            )

    def test_empty_source_branch_raises(self):
        with pytest.raises(ValidationError):
            CreatePullRequestInput(
                project="p", repository_id="r",
                source_branch="", target_branch="main", title="PR"
            )


class TestUpdatePullRequestInput:
    def test_valid_all_none(self):
        m = UpdatePullRequestInput(project="p", repository_id="r", pull_request_id=1)
        assert m.title is None
        assert m.description is None
        assert m.status is None
        assert m.auto_complete is None

    def test_valid_with_fields(self):
        m = UpdatePullRequestInput(
            project="p", repository_id="r", pull_request_id=7,
            title="Updated", status="completed", auto_complete=True
        )
        assert m.title == "Updated"
        assert m.auto_complete is True

    def test_zero_pr_id_raises(self):
        with pytest.raises(ValidationError):
            UpdatePullRequestInput(project="p", repository_id="r", pull_request_id=0)


# ===========================================================================
# TOOL TESTS — tools/git.py
# ===========================================================================


@pytest.fixture(autouse=True)
def reset_client():
    """Reset the module-level _client before each test."""
    git_tools._client = None
    yield
    git_tools._client = None


class TestRegister:
    def test_register_sets_client_and_registers_tools(self):
        mock_mcp = MagicMock()
        mock_mcp.tool = MagicMock(return_value=lambda fn: fn)
        client = _make_mock_client()

        git_tools.register(mock_mcp, client)

        assert git_tools._client is client
        assert mock_mcp.tool.call_count == 10

    def test_register_tool_names(self):
        registered_names = []
        mock_mcp = MagicMock()
        mock_mcp.tool = lambda name, description: (
            registered_names.append(name) or (lambda fn: fn)
        )
        git_tools.register(mock_mcp, _make_mock_client())

        expected = [
            "azdevops_list_repositories",
            "azdevops_get_repository",
            "azdevops_list_branches",
            "azdevops_get_file_content",
            "azdevops_list_commits",
            "azdevops_get_commit",
            "azdevops_list_pull_requests",
            "azdevops_get_pull_request",
            "azdevops_create_pull_request",
            "azdevops_update_pull_request",
        ]
        assert registered_names == expected


class TestListRepositories:
    async def test_success_returns_json(self):
        client = _make_mock_client()
        client.get.return_value = [{"id": "abc", "name": "my-repo"}]
        git_tools._client = client

        result = await git_tools.azdevops_list_repositories(project="myproject")
        data = json.loads(result)

        assert isinstance(data, list)
        assert data[0]["name"] == "my-repo"
        client.get.assert_called_once_with(
            "git/repositories", project="myproject", params={"$top": 20}
        )

    async def test_custom_limit_passed(self):
        client = _make_mock_client()
        client.get.return_value = []
        git_tools._client = client

        await git_tools.azdevops_list_repositories(project="p", limit=5)
        client.get.assert_called_once_with(
            "git/repositories", project="p", params={"$top": 5}
        )

    async def test_401_returns_error_message(self):
        client = _make_mock_client()
        client.get.side_effect = _make_status_error(401)
        git_tools._client = client

        result = await git_tools.azdevops_list_repositories(project="p")
        assert "authentication" in result.lower() or "credentials" in result.lower()

    async def test_timeout_returns_error_message(self):
        client = _make_mock_client()
        client.get.side_effect = httpx.ReadTimeout("timed out")
        git_tools._client = client

        result = await git_tools.azdevops_list_repositories(project="p")
        assert "timed out" in result.lower() or "timeout" in result.lower()

    async def test_request_error_returns_error_message(self):
        client = _make_mock_client()
        client.get.side_effect = httpx.ConnectError("connection refused")
        git_tools._client = client

        result = await git_tools.azdevops_list_repositories(project="p")
        assert "network" in result.lower() or "error" in result.lower()


class TestGetRepository:
    async def test_success(self):
        client = _make_mock_client()
        client.get.return_value = {"id": "repo-1", "name": "repo"}
        git_tools._client = client

        result = await git_tools.azdevops_get_repository(project="p", repository_id="repo-1")
        data = json.loads(result)
        assert data["name"] == "repo"

    async def test_404_returns_error_message(self):
        client = _make_mock_client()
        client.get.side_effect = _make_status_error(404)
        git_tools._client = client

        result = await git_tools.azdevops_get_repository(project="p", repository_id="bad-id")
        assert "not found" in result.lower()


class TestListBranches:
    async def test_success(self):
        client = _make_mock_client()
        client.get.return_value = {"value": [{"name": "refs/heads/main"}]}
        git_tools._client = client

        result = await git_tools.azdevops_list_branches(project="p", repository_id="r")
        data = json.loads(result)
        assert "value" in data

    async def test_limit_forwarded(self):
        client = _make_mock_client()
        client.get.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_list_branches(project="p", repository_id="r", limit=10)
        _, kwargs = client.get.call_args
        assert kwargs["params"]["$top"] == 10


class TestGetFileContent:
    async def test_success_no_branch(self):
        mock_response = MagicMock()
        mock_response.text = "print('hello')"
        client = _make_mock_client()
        client.request_raw.return_value = mock_response
        git_tools._client = client

        result = await git_tools.azdevops_get_file_content(
            project="p", repository_id="r", file_path="/src/main.py"
        )
        data = json.loads(result)
        assert data["content"] == "print('hello')"
        assert data["path"] == "/src/main.py"

        _, kwargs = client.request_raw.call_args
        assert "versionDescriptor.version" not in kwargs.get("params", {})

    async def test_success_with_branch(self):
        mock_response = MagicMock()
        mock_response.text = "# README"
        client = _make_mock_client()
        client.request_raw.return_value = mock_response
        git_tools._client = client

        await git_tools.azdevops_get_file_content(
            project="p", repository_id="r", file_path="/README.md", branch="main"
        )
        _, kwargs = client.request_raw.call_args
        assert kwargs["params"]["versionDescriptor.version"] == "main"

    async def test_404_returns_error(self):
        client = _make_mock_client()
        client.request_raw.side_effect = _make_status_error(404)
        git_tools._client = client

        result = await git_tools.azdevops_get_file_content(
            project="p", repository_id="r", file_path="/missing.py"
        )
        assert "not found" in result.lower()


class TestListCommits:
    async def test_success_minimal(self):
        client = _make_mock_client()
        client.get.return_value = {"value": [{"commitId": "abc123"}]}
        git_tools._client = client

        result = await git_tools.azdevops_list_commits(project="p", repository_id="r")
        data = json.loads(result)
        assert data["value"][0]["commitId"] == "abc123"

    async def test_all_filters_forwarded(self):
        client = _make_mock_client()
        client.get.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_list_commits(
            project="p", repository_id="r",
            branch="main", author="alice",
            from_date="2024-01-01", to_date="2024-06-30",
            path="/src", limit=5,
        )
        _, kwargs = client.get.call_args
        params = kwargs["params"]
        assert params["searchCriteria.itemVersion.version"] == "main"
        assert params["searchCriteria.author"] == "alice"
        assert params["searchCriteria.fromDate"] == "2024-01-01"
        assert params["searchCriteria.toDate"] == "2024-06-30"
        assert params["searchCriteria.itemPath"] == "/src"
        assert params["$top"] == 5

    async def test_optional_filters_absent_when_none(self):
        client = _make_mock_client()
        client.get.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_list_commits(project="p", repository_id="r")
        _, kwargs = client.get.call_args
        params = kwargs["params"]
        assert "searchCriteria.itemVersion.version" not in params
        assert "searchCriteria.author" not in params


class TestGetCommit:
    async def test_success(self):
        client = _make_mock_client()
        client.get.return_value = {"commitId": "deadbeef", "comment": "fix bug"}
        git_tools._client = client

        result = await git_tools.azdevops_get_commit(
            project="p", repository_id="r", commit_id="deadbeef"
        )
        data = json.loads(result)
        assert data["commitId"] == "deadbeef"

    async def test_404_returns_error(self):
        client = _make_mock_client()
        client.get.side_effect = _make_status_error(404)
        git_tools._client = client

        result = await git_tools.azdevops_get_commit(
            project="p", repository_id="r", commit_id="bad"
        )
        assert "not found" in result.lower()


class TestListPullRequests:
    async def test_success(self):
        client = _make_mock_client()
        client.get.return_value = {"value": [{"pullRequestId": 1}]}
        git_tools._client = client

        result = await git_tools.azdevops_list_pull_requests(project="p", repository_id="r")
        data = json.loads(result)
        assert data["value"][0]["pullRequestId"] == 1

    async def test_creator_and_reviewer_forwarded(self):
        client = _make_mock_client()
        client.get.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_list_pull_requests(
            project="p", repository_id="r", creator="alice", reviewer="bob"
        )
        _, kwargs = client.get.call_args
        params = kwargs["params"]
        assert params["searchCriteria.creatorId"] == "alice"
        assert params["searchCriteria.reviewerId"] == "bob"

    async def test_optional_filters_absent_when_none(self):
        client = _make_mock_client()
        client.get.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_list_pull_requests(project="p", repository_id="r")
        _, kwargs = client.get.call_args
        params = kwargs["params"]
        assert "searchCriteria.creatorId" not in params
        assert "searchCriteria.reviewerId" not in params

    async def test_429_returns_rate_limit_message(self):
        client = _make_mock_client()
        client.get.side_effect = _make_status_error(429)
        git_tools._client = client

        result = await git_tools.azdevops_list_pull_requests(project="p", repository_id="r")
        assert "rate limit" in result.lower()


class TestGetPullRequest:
    async def test_success(self):
        client = _make_mock_client()
        client.get.return_value = {"pullRequestId": 42, "title": "My PR"}
        git_tools._client = client

        result = await git_tools.azdevops_get_pull_request(
            project="p", repository_id="r", pull_request_id=42
        )
        data = json.loads(result)
        assert data["pullRequestId"] == 42

    async def test_404_returns_error(self):
        client = _make_mock_client()
        client.get.side_effect = _make_status_error(404)
        git_tools._client = client

        result = await git_tools.azdevops_get_pull_request(
            project="p", repository_id="r", pull_request_id=999
        )
        assert "not found" in result.lower()


class TestCreatePullRequest:
    async def test_success_minimal(self):
        client = _make_mock_client()
        client.post.return_value = {"pullRequestId": 10, "title": "New PR"}
        git_tools._client = client

        result = await git_tools.azdevops_create_pull_request(
            project="p", repository_id="r",
            source_branch="feature/x", target_branch="main", title="New PR"
        )
        data = json.loads(result)
        assert data["pullRequestId"] == 10

        _, kwargs = client.post.call_args
        body = kwargs["json"]
        assert body["sourceRefName"] == "refs/heads/feature/x"
        assert body["targetRefName"] == "refs/heads/main"
        assert body["title"] == "New PR"
        assert "description" not in body
        assert "reviewerIds" not in body

    async def test_success_with_description_and_reviewers(self):
        client = _make_mock_client()
        client.post.return_value = {"pullRequestId": 11}
        git_tools._client = client

        await git_tools.azdevops_create_pull_request(
            project="p", repository_id="r",
            source_branch="feat", target_branch="main",
            title="PR", description="fixes #1", reviewer=["alice", "bob"]
        )
        _, kwargs = client.post.call_args
        body = kwargs["json"]
        assert body["description"] == "fixes #1"
        assert len(body["reviewerIds"]) == 2
        assert body["reviewerIds"][0] == {"uniqueName": "alice"}

    async def test_403_returns_permission_error(self):
        client = _make_mock_client()
        client.post.side_effect = _make_status_error(403)
        git_tools._client = client

        result = await git_tools.azdevops_create_pull_request(
            project="p", repository_id="r",
            source_branch="feat", target_branch="main", title="PR"
        )
        assert "permission" in result.lower()


class TestUpdatePullRequest:
    async def test_success_updates_title_and_status(self):
        client = _make_mock_client()
        client.patch.return_value = {"pullRequestId": 5, "title": "Updated"}
        git_tools._client = client

        result = await git_tools.azdevops_update_pull_request(
            project="p", repository_id="r", pull_request_id=5,
            title="Updated", status="completed"
        )
        data = json.loads(result)
        assert data["title"] == "Updated"

        _, kwargs = client.patch.call_args
        body = kwargs["json"]
        assert body["title"] == "Updated"
        assert body["status"] == "completed"

    async def test_none_fields_not_sent(self):
        client = _make_mock_client()
        client.patch.return_value = {}
        git_tools._client = client

        await git_tools.azdevops_update_pull_request(
            project="p", repository_id="r", pull_request_id=5
        )
        _, kwargs = client.patch.call_args
        body = kwargs["json"]
        assert body == {}

    async def test_409_returns_conflict_message(self):
        client = _make_mock_client()
        client.patch.side_effect = _make_status_error(409)
        git_tools._client = client

        result = await git_tools.azdevops_update_pull_request(
            project="p", repository_id="r", pull_request_id=5, title="x"
        )
        assert "conflict" in result.lower()