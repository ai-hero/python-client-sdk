from .automation import Automation
from .exceptions import AIHeroException


class ItemRecommendation(Automation):
    def get_recommendations(self, item_id):
        if item_id is None or item_id.strip() == "":
            raise AIHeroException("item_id cannot be null or empty.")
        return super().infer("get_recommendations", {"thing_id": item_id})
