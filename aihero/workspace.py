from .exceptions import AIHeroException
from time import sleep


class Workspace:
    """Abstraction for workspace operations"""

    def __init__(self, api):
        self._api = api

    def get_automations(self):
        return self._api.get(
            self._api.endpoint("workspace", "automations"),
            error_msg="Couldn't get the automations.",
            network_errors={
                403: f"Could not connect to workspace. Please check the auth_secret."
            },
        )

    def get_automation(self, automation_id):
        _ = self._api.get(
            self._api.endpoint("workspace", "automations", automation_id),
            error_msg="Couldn't get the automation.",
            network_errors={
                403: f"Could not connect to workspace. Please check the auth_secret."
            },
        )
        api_keys = self._api.get(
            self._api.endpoint("workspace", "automations", automation_id, "api_keys"),
            error_msg="Couldn't get the automation api_key.",
            network_errors={
                403: f"Could not connect to workspace. Please check the auth_secret."
            },
        )
