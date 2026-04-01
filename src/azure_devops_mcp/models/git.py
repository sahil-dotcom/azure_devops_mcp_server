from pydantic import BaseModel, ConfigDict, Field

class listRepositoriesInput(BaseModel):
    """Input model for listing Git repositories in an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    limit: int = Field(default=20, ge=1, le=100)

class getRepositoryInput(BaseModel):
    """Input model for retrieving a specific Git repository in an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1, description="Name or ID of the repository to retrieve")

class listBranchesInput(BaseModel):
    """Input model for listing branches in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1, description="Name or ID of the repository to list branches for")
    limit: int = Field(default=20, ge=1, le=100)

class getFileContentInput(BaseModel):
    """Input model for retrieving the content of a file in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1, description="Name or ID of the repository containing the file")
    file_path: str = Field(..., min_length=1, description="Path to the file within the repository")
    branch: str | None = None

class ListCommitsInput(BaseModel):
    """Input model for listing commits in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    branch: str | None = None
    author: str | None = None
    from_data: str | None = None
    to_date: str | None = None
    path: str | None = None
    limit: int = Field(default=20, ge=1, le=100)

class GetCommitInput(BaseModel):
    """Input model for retrieving a specific commit in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    commit_id: str = Field(..., min_length=1, description="ID of the commit to retrieve")

class ListPullRequestsInput(BaseModel):
    """Input model for listing pull requests in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    status: str | None = None
    creator: str | None = None
    reviewer: str | None = None
    limit: int = Field(default=20, ge=1, le=100)

class GetPullRequestInput(BaseModel):
    """Input model for retrieving a specific pull request in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    pull_request_id: int = Field(..., gt=0) 

class CreatePullRequestInput(BaseModel):
    """Input model for creating a pull request in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    source_branch: str = Field(..., min_length=1)
    target_branch: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str | None = None
    reviewer: list[str] | None = None

class UpdatePullRequestInput(BaseModel):
    """Input model for updating a pull request in a Git repository within an Azure DevOps project."""
    model_config = ConfigDict(str_strip_whitesapce=True, extra="forbid")

    project: str = Field(..., min_length=1)
    repository_id: str = Field(..., min_length=1)
    pull_request_id: int = Field(..., gt=0)
    title: str | None = None
    description: str | None = None
    status: str | None = None
    auto_complete: bool | None = None