from .exceptions import AIHeroException
from time import sleep


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

    def _sync_job(self, job):
        job = self._api.post(
            self._api.endpoint("automations", self._automation_id, "jobs"),
            job,
            error_msg=f"Unknown error in job.",
            network_errors={
                400: f"Please check the job parameters.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )
        while True:
            sleep(0.1)
            job = self._api.get(
                self._api.endpoint(
                    "automations", self._automation_id, "jobs", job["_id"]
                ),
                error_msg=f"Unknown error in job.",
                network_errors={
                    400: f"Please check the request.",
                    403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
                },
            )
            if "state" not in job:
                continue
            state = job["state"]
            if state == "created":
                pass
            elif state not in ["done", "continue", "error"]:
                pass
            elif state == "error":
                raise AIHeroException("Error while uploading data")
            elif state in ["done"]:
                break

    def _infer(self, task, obj):
        return self._api.post(
            self._api.endpoint("automations", self._automation_id, "inferences", task),
            obj,
            error_msg=f"Unknown error in {task}.",
            network_errors={
                400: f"Please check the data uploaded.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )
