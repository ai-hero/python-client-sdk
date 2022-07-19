from .api import Api
from .automation import Automation, construct
from .workspace import Workspace


class Client:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, server_url=None):
        self._api = Api(server_url=server_url)

    def ping(self):
        return self._api.get(
            self._api.ping_endpoint(),
            error_msg="Could not connect to the server {self._api.server_url}",
        )

    def get_automation(self, automation_id, api_key):
        automation = Automation(
            automation_id=automation_id,
            api=Api(api_key=api_key, server_url=self._api.server_url),
        )
        automation_definition = automation.get_definition()
        automation_type = automation_definition["type"]
        automation_api = Api(api_key=api_key, server_url=self._api.server_url)
        automation = construct(
            automation_type=automation_type,
            automation_id=automation_id,
            automation_api=automation_api,
        )
        return automation

    def request_auth_secret(self, email):
        path = f"{self._api.endpoint('users', 'auth_secret')}?email={email}"
        self._api.get(path)

    def get_workspace(self, auth_secret):
        workspace = Workspace(
            api=Api(auth_secret=auth_secret, server_url=self._api.server_url),
        )
        _ = workspace.get_automations()
        return workspace
