from .exceptions import AIHeroException


class Automation:
    """Abstraction for automation operations"""

    def __init__(self, automation_id, api):
        if automation_id is None or automation_id.strip() == "":
            raise AIHeroException("automation_id cannot be null or empty.")
        self._api = api
        self._automation_id = automation_id

    def get_definition(self):
        return self._api.get(
            self._api.endpoint("automations", self._automation_id, "definition"),
            error_msg="Couldn't get the definition.",
            network_errors={
                403: f"Could not connect to automation {self._automation_id}. Please check the API key."
            },
        )

    def infer(self, task, obj):
        return self._api.post(
            self._api.endpoint("automations", self._automation_id, "inferences", task),
            obj,
            error_msg=f"Unknown error in {task}.",
            network_errors={
                400: f"Please check the data uploaded.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )
