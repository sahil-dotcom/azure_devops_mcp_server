from typing import Protocol, runtime_checkable
from .pat import PATAuth
from .oauth import OAuthAuth

@runtime_checkable
class AuthProvider(Protocol):
    """Protocol for providing authentication headers."""
    async def get_headers(self) -> dict[str, str]:
        """Asynchronously retrieves authentication headers."""

__all__ = ["AuthProvider", "PATAuth", "OAuthAuth"]