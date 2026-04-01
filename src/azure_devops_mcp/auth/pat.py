'''
Personal Access Token (PAT) authentication for Azure DevOps.
'''
import base64

class PATAuth:
    '''Authentication via base64-encoded Personal Access Token (PAT).'''
    def __init__(self, pat:str) -> None:
        token = base64.b64encode(f":{pat}".encode()).decode("ascii")
        self.header = {"Authorization": f"Basic {token}"}

    async def get_headers(self) -> dict[str, str]:
        '''Return Authorization headers using the stored PAT'''
        return self.header