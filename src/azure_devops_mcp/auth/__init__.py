"""Authentication provider protocol and imports for Azure DevOps MCP."""

from typing import Protocol, runtime_checkable

from .oauth import OAuthAuth
from .pat import PATAuth


@runtime_checkable
class AuthProvider(Protocol):
    """Protocol for providing authentication headers."""

    async def get_headers(self) -> dict[str, str]:
        """Asynchronously retrieves authentication headers."""


__all__ = ["AuthProvider", "PATAuth", "OAuthAuth"]
