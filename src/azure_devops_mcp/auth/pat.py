"""
Personal Access Token (PAT) authentication for Azure DevOps.

This module provides the PATAuth class for authenticating Azure DevOps API requests
using a base64-encoded Personal Access Token (PAT).

Example:
    pat_auth = PATAuth(pat)
    headers = await pat_auth.get_headers()
"""

import base64


class PATAuth:
    """
    Authentication via base64-encoded Personal Access Token (PAT).

    This class encodes a PAT and provides authorization headers for Azure DevOps
    REST API requests.

    Attributes:
        header (dict[str, str]): The authorization header with the encoded PAT.
    """

    def __init__(self, pat: str) -> None:
        """Initializes the PATAuth instance.

        Args:
            pat (str): The Personal Access Token for Azure DevOps.
        """
        token = base64.b64encode(f":{pat}".encode()).decode("ascii")
        self.header = {"Authorization": f"Basic {token}"}

    async def get_headers(self) -> dict[str, str]:
        """
        Return the Authorization headers using the stored PAT.

        Returns:
            dict[str, str]: A dictionary containing the Authorization header.
        """
        return self.header
