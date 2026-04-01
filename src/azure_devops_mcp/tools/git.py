import json
import httpx
from azure_devops_mcp.shared.error import handle_api_error
from azure_devops_mcp.client import AzureDevOpsClient
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
_client: AzureDevOpsClient | None = None

def register(mcp, client: AzureDevOpsClient) -> None:
    global _client
    _client = client

    mcp.tool(
        name="azdevops_list_repositories",
        description="List Git repositories in an Azure DevOps project",
    )(azdevops_list_repositories)

    mcp.tool(
        name="azdevops_get_repository",
        description="Get a specific Git repository in an Azure DevOps project",
    )(azdevops_get_repository)

    mcp.tool(
        name="azdevops_list_branches",
        description="List branches in a Git repository within an Azure DevOps project",
    )(azdevops_list_branches)

    mcp.tool(
        name="azdevops_get_file_content",
        description="Get the content of a file in a Git repository within an Azure DevOps project",
    )(azdevops_get_file_content)

    mcp.tool(
        name="azdevops_list_commits",
        description="List commits in a Git repository within an Azure DevOps project",
    )(azdevops_list_commits)

    mcp.tool(
        name="azdevops_get_commit",
        description="Get a specific commit in a Git repository within an Azure DevOps project",
    )(azdevops_get_commit)

    mcp.tool(
        name="azdevops_list_pull_requests",
        description="List pull requests in a Git repository within an Azure DevOps project",
    )(azdevops_list_pull_requests)

    mcp.tool(
        name="azdevops_get_pull_request",
        description="Get a specific pull request in a Git repository within an Azure DevOps project",
    )(azdevops_get_pull_request)

    mcp.tool(
        name="azdevops_create_pull_request",
        description="Create a pull request in a Git repository within an Azure DevOps project",
    )(azdevops_create_pull_request)

    mcp.tool(
        name="azdevops_update_pull_request",
        description="Update a pull request in a Git repository within an Azure DevOps project",
    )(azdevops_update_pull_request)


async def azdevops_list_repositories(
    project: str, limit: int = 20
) -> str:
    """List Git repositories in an Azure DevOps project."""
    inp = listRepositoriesInput(project=project, limit=limit)
    try:
        data = await _client.get(
            "git/repositories",
            project=inp.project,
            params={"$top": inp.limit},
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_get_repository(
    project: str, repository_id: str
) -> str:
    """Get a specific Git repository in an Azure DevOps project."""
    inp = getRepositoryInput(project=project, repository_id=repository_id)
    try:
        data = await _client.get(
            f"git/repositories/{inp.repository_id}",
            project=inp.project,
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_list_branches(
    project: str, repository_id: str, limit: int = 20
) -> str:
    """List branches in a Git repository within an Azure DevOps project."""
    inp = listBranchesInput(project=project, repository_id=repository_id, limit=limit)
    try:
        data = await _client.get(
            f"git/repositories/{inp.repository_id}/refs",
            project=inp.project,
            params={"$top": inp.limit},
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_get_file_content(
    project: str,
    repository_id: str,
    file_path: str,
    branch: str | None = None
) -> str:
    """Get the content of a file in a Git repository within an Azure DevOps project."""
    inp = getFileContentInput(
        project=project,
        repository_id=repository_id,
        file_path=file_path,
        branch=branch,
    )
    try:
        params: dict = {"path": inp.file_path}
        if inp.branch:
            params["versionDescriptor.version"] = inp.branch
        response = await _client.request_raw(
            "GET",
            f"git/repositories/{inp.repository_id}/items",
            project=inp.project,
            params=params,
        )
        content = response.text
        return json.dumps({"path": inp.file_path, "content": content}, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_list_commits(
    project: str,
    repository_id: str,
    branch: str | None = None,
    author: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    path: str | None = None,
    limit: int = 20,
) -> str:
    """List commits in a Git repository within an Azure DevOps project."""
    inp = ListCommitsInput(
        project=project,
        repository_id=repository_id,
        branch=branch,
        author=author,
        from_data=from_date,
        to_date=to_date,
        path=path,
        limit=limit,
    )
    try:
        params: dict = {"$top": inp.limit}
        if inp.branch:
            params["searchCriteria.itemVersion.version"] = inp.branch
        if inp.author:
            params["searchCriteria.author"] = inp.author
        if inp.from_data:
            params["searchCriteria.fromDate"] = inp.from_data
        if inp.to_date:
            params["searchCriteria.toDate"] = inp.to_date
        if inp.path:
            params["searchCriteria.itemPath"] = inp.path

        data = await _client.get(
            f"git/repositories/{inp.repository_id}/commits",
            project=inp.project,
            params=params,
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_get_commit(
    project: str, repository_id: str, commit_id: str
) -> str:
    """Get a specific commit in a Git repository within an Azure DevOps project."""
    inp = GetCommitInput(project=project, repository_id=repository_id, commit_id=commit_id)
    try:
        data = await _client.get(
            f"git/repositories/{inp.repository_id}/commits/{inp.commit_id}",
            project=inp.project,
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_list_pull_requests(
    project: str,
    repository_id: str,
    status: str | None = None,
    creator: str | None = None,
    reviewer: str | None = None,
    limit: int = 20,
) -> str:
    """List pull requests in a Git repository within an Azure DevOps project."""
    inp = ListPullRequestsInput(
        project=project, 
        repository_id=repository_id, 
        status=status, 
        creator=creator, 
        reviewer=reviewer, 
        limit=limit,
    )
    try:
        params = {
            "$top": inp.limit,
            "searchCriteria.status": inp.status,
        }
        if inp.creator:
            params["searchCriteria.creatorId"] = inp.creator
        if inp.reviewer:
            params["searchCriteria.reviewerId"] = inp.reviewer
        data = await _client.get(
            f"git/repositories/{inp.repository_id}/pullrequests",
            project=inp.project,
            params=params,
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_get_pull_request(
    project: str,
    repository_id: str,
    pull_request_id: int,
) -> str:
    """Get a specific pull request in a Git repository within an Azure DevOps project."""
    inp = GetPullRequestInput(
        project=project,
        repository_id=repository_id,
        pull_request_id=pull_request_id
    )
    try:
        data = await _client.get(
            f"git/repositories/{inp.repository_id}/pullrequests/{inp.pull_request_id}",
            project=inp.project,
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)
async def azdevops_create_pull_request(
    project: str,
    repository_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str | None = None,
    reviewer: list[str] | None = None,
) -> str:
    """Create a pull request in a Git repository within an Azure DevOps project."""
    inp = CreatePullRequestInput(
        project=project,
        repository_id=repository_id,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title,
        description=description,
        reviewer=reviewer
    )
    try:
        body = dict = {
            "sourceRefName": f"refs/heads/{inp.source_branch}",
            "targetRefName": f"refs/heads/{inp.target_branch}",
            "title": inp.title,
        }
        if inp.description:
            body["description"] = inp.description
        if inp.reviewer:
            body["reviewerIds"] = [
                {"uniqueName": r} for r in inp.reviewer
            ]
        data = await _client.post(
            f"git/repositories/{inp.repository_id}/pullrequests",
            project=inp.project,
            json=body
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)

async def azdevops_update_pull_request(
    project: str,
    repository_id: str,
    pull_request_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    auto_complete: bool | None = None,
) -> str:
    """Update a pull request in a Git repository within an Azure DevOps project."""
    inp = UpdatePullRequestInput(
        project=project,
        repository_id=repository_id,
        pull_request_id=pull_request_id,
        title=title,
        description=description,
        status=status,
        auto_complete=auto_complete
    )
    try:
        body: dict = {}
        if inp.status:
            body["status"] = inp.status
        if inp.title:
            body["title"] = inp.title
        if inp.description:
            body["description"] = inp.description
        if inp.auto_complete is not None:
            body["autoCompleteSetBy"] = {} if inp.auto_complete else None

        data = await _client.patch(
            f"git/repositories/{inp.repository_id}/pullrequests/{inp.pull_request_id}",
            project=inp.project,
            json=body
        )
        return json.dumps(data, indent=2)
    except httpx.HTTPStatusError as e:
        return handle_api_error(e)
    except httpx.RequestError as e:
        return handle_api_error(e)
    except httpx.TimeoutException as e:
        return handle_api_error(e)