"""Application settings loaded from environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Azure DevOps connection and authentication settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AZURE_DEVOPS_",
        extra="ignore",
        env_file_encoding="utf-8",
    )

    org_url: str
    pat: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    tenant_id: str | None = None
    api_version: str = "7.1"

    @property
    def auth_method(self) -> str:
        """Return the active authentication method."""
        if self.pat:
            return "PAT"
        if self.client_id and self.client_secret and self.tenant_id:
            return "oauth"
        raise ValueError("No valid authentication method configured. Please provide either a PAT or OAuth credentials.")

    @model_validator(mode="after")
    def _validate_auth(self) -> "Settings":
        """Validate that the necessary authentication information is provided."""
        has_pat = bool(self.pat)
        has_oauth = bool (
            self.client_id
            and self.client_secret
            and self.tenant_id
        )
        if not has_pat and not has_oauth:
            raise ValueError("No valid authentication method configured. Please provide either a PAT or OAuth credentials.")
        return self