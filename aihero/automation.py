from .api import Api
from .exceptions import AIHeroException
from time import sleep

COLORS = [
    "red",
    "orange",
    "amber",
    "yellow",
    "lime",
    "green",
    "emerald",
    "teal",
    "cyan",
    "sky",
    "blue",
    "indigo",
    "violet",
    "purple",
    "fuscia",
]

AUTOMATION_TYPES = [
    "detect_sentiment",
    "tag_short_text",
    "tag_entire_images",
    "recommend_items_to_people",
    "recommend_people_to_each_other",
    "recommend_people_from_two_groups_to_each_other",
]


class Automation:
    """Abstraction for automation operations"""

    def __init__(self, automation_id, api):
        if automation_id is None or automation_id.strip() == "":
            raise AIHeroException("automation_id cannot be null or empty.")
        self._api = api
        self._automation_id = automation_id

    def get_definition(self) -> dict:
        return self._api.get(
            self._api.endpoint("automations", self._automation_id, "definition"),
            error_msg="Couldn't get the definition.",
            network_errors={
                403: f"Could not connect to automation {self._automation_id}. Please check the API key."
            },
        )

    def update_ontology(self, ontology: list) -> dict:
        return self._api.post(
            self._api.endpoint(
                "automations", self._automation_id, "definition", "ontology"
            ),
            ontology,
            error_msg="Unknown error in updating ontology.",
            network_errors={
                400: "Please check the ontology to be updated.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )

    def _sync_job(self, job: dict):
        job = self._api.post(
            self._api.endpoint("automations", self._automation_id, "jobs"),
            job,
            error_msg="Unknown error in job.",
            network_errors={
                400: "Please check the job parameters.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )
        while True:
            sleep(0.1)
            job = self._api.get(
                self._api.endpoint(
                    "automations", self._automation_id, "jobs", job["_id"]
                ),
                error_msg="Unknown error in job.",
                network_errors={
                    400: "Please check the request.",
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

    def _async_job(self, job: dict) -> dict:
        job = self._api.post(
            self._api.endpoint("automations", self._automation_id, "jobs"),
            job,
            error_msg="Unknown error in job.",
            network_errors={
                400: "Please check the job parameters.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )
        return job

    def _infer(self, task: str, obj: dict) -> dict:
        return self._api.post(
            self._api.endpoint("automations", self._automation_id, "inferences", task),
            obj,
            error_msg="Unknown error in {task}.",
            network_errors={
                400: "Please check the data uploaded.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )

    def understand(self) -> dict:
        return self._async_job({"type": "understand"})

    def get_job(self, job) -> dict:
        return self._api.get(
            self._api.endpoint("automations", self._automation_id, "jobs", job["_id"]),
            error_msg="Unknown error in job.",
            network_errors={
                400: "Please check the request.",
                403: f"Could not connect to automation {self._automation_id}. Please check the API key.",
            },
        )


def construct(
    automation_type: str, automation_id: str, automation_api: Api
) -> Automation:
    from .detect_sentiment import DetectSentiment
    from .tag_short_text import TagShortText
    from .tag_entire_images import TagEntireImages
    from .recommend_people_to_each_other import RecommendPeopleToEachOther
    from .recommend_people_from_two_groups_to_each_other import (
        RecommendPeopleFromTwoGroupsToEachOther,
    )
    from .recommend_items_to_people import RecommendItemsToPeople

    AUTOMATION_CLASSES = {
        "detect_sentiment": DetectSentiment,
        "tag_short_text": TagShortText,
        "tag_entire_images": TagEntireImages,
        "recommend_items_to_people": RecommendItemsToPeople,
        "recommend_people_to_each_other": RecommendPeopleToEachOther,
        "recommend_people_from_two_groups_to_each_other": RecommendPeopleFromTwoGroupsToEachOther,
    }

    if automation_type not in AUTOMATION_CLASSES:
        raise AIHeroException(
            f"Unsupported automation type for the API: {automation_type}"
        )
    return AUTOMATION_CLASSES[automation_type](
        automation_id=automation_id, api=automation_api
    )
