from aihero.exceptions import AIHeroException
from .automation import AUTOMATION_TYPES


class Workspace:
    """Abstraction for workspace operations"""

    def __init__(self, api):
        self._api = api

    def get_automations(self):
        return self._api.get(
            self._api.endpoint("workspace", "automations"),
            error_msg="Couldn't get the automations.",
            network_errors={
                403: "Could not connect to workspace. Please check the auth_secret."
            },
        )

    def create_automation(
        self, automation_type: str, name: str = None, description: str = None
    ):
        if automation_type not in AUTOMATION_TYPES:
            raise AIHeroException(
                f"Unknown/unsupported automation type {automation_type}"
            )
        obj = {"type": automation_type, "name": "auto2", "description": "Bar"}
        if name:
            obj["name"] = name
        if description:
            obj["description"] = description

        automation = self._api.post(
            self._api.endpoint("workspace", "automations"),
            obj=obj,
            error_msg="Couldn't create the automation api_key.",
            network_errors={
                403: "Could not create api key. Please check the auth_secret."
            },
        )
        return self.get_automation(automation["_id"])

    def get_automation(self, automation_id):
        api_keys = self._api.get(
            self._api.endpoint("workspace", "automations", automation_id, "api_keys"),
            error_msg="Couldn't get the automation api_key.",
            network_errors={
                403: "Could not get api key. Please check the auth_secret."
            },
        )
        if not api_keys:
            print(
                "Did not find an existing API key for the automation. Creating an API key."
            )
            self._api.post(
                self._api.endpoint(
                    "workspace", "automations", automation_id, "api_keys"
                ),
                obj={},
                error_msg="Couldn't create the automation api_key.",
                network_errors={
                    403: "Could not create api key. Please check the auth_secret."
                },
            )
            api_keys = self._api.get(
                self._api.endpoint(
                    "workspace", "automations", automation_id, "api_keys"
                ),
                error_msg="Couldn't get the automation api_key.",
                network_errors={
                    403: "Could not get api key. Please check the auth_secret."
                },
            )
        api_key = api_keys[0]["key"]
        from . import Client

        client = Client(server_url=self._api.server_url)
        return client.get_automation(automation_id=automation_id, api_key=api_key)
