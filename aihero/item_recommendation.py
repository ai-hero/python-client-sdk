from .automation import Automation
from .exceptions import AIHeroException


class ItemRecommendation(Automation):
    def add(self, item, guid):
        if item is None or len(item) == 0:
            raise AIHeroException(
                "You need to provide the image to teach the automation with."
            )
        if guid is None or guid.strip() == "":
            raise AIHeroException(
                "You need to provide the guid to teach the automation with."
            )

        item["guid"] = guid
        return super()._sync_job({"type": "ingest_row", "row": item})

    def get_recommendations(self, item_id):
        if item_id is None or item_id.strip() == "":
            raise AIHeroException("item_id cannot be null or empty.")
        return super()._infer("get_recommendations", {"thing_id": item_id})
