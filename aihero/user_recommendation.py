from .automation import Automation
from .exceptions import AIHeroException


class UserRecommendation(Automation):
    def get_recommendations(self, person_id):
        if person_id is None or person_id.strip() == "":
            raise AIHeroException("person_id cannot be null or empty.")
        return super().infer("get_recommendations", {"thing_id": person_id})
