from .automation import Automation


class RecommendItemsToPeople(Automation):
    def add_item(self, item: dict, guid: str) -> dict:
        assert item is not None
        assert guid is not None
        item["guid"] = guid
        return super()._sync_job({"type": "add_item", "row": item})

    def add_person(self, person: dict, guid: str) -> dict:
        assert person is not None
        assert guid is not None
        person["guid"] = guid
        return super()._sync_job({"type": "add_person", "row": person})

    def add_action(
        self,
        person_guid: str,
        item_guid: str,
        action_type: str,
        session_id: str = None,
        timestamp: int = None,
        duration: float = None,
        rating: float = None,
    ) -> dict:
        assert person_guid is not None
        assert item_guid is not None
        assert action_type is not None
        return super()._sync_job(
            {
                "type": "add_action",
                "action": {
                    "person_guid": person_guid,
                    "item_guid": item_guid,
                    "action_type": action_type,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "duration": duration,
                    "rating": rating,
                },
            }
        )

    def add_preference(self, person_guid: str, preference: list) -> dict:
        assert person_guid is not None
        assert preference is not None
        return super()._sync_job(
            {
                "type": "add_preference",
                "action": {
                    "person_guid": person_guid,
                    "preference": preference,
                },
            }
        )

    def get_recommendations(self, guid: str) -> dict:
        assert guid is not None
        return super()._infer("get_recommendations", {"guid": guid})
