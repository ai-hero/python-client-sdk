from .exceptions import AIHeroException
from time import sleep


class Workspace:
    """Abstraction for workspace operations"""

    def __init__(self, api):
        self._api = api

    def get_automations(self):
        return self._api.get(
            self._api.endpoint("workspace", "automations"),
            error_msg="Couldn't get the definition.",
            network_errors={
                403: f"Could not connect to workspace. Please check the auth_secret."
            },
        )
