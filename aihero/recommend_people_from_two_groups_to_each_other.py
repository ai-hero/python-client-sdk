from .automation import Automation
from .exceptions import AIHeroException


class RecommendPeopleFromTwoGroupsToEachOther(Automation):
    def add_person_to_group_one(self, person, guid):
        if person is None or len(person) == 0:
            raise AIHeroException(
                "You need to provide the image to teach the automation with."
            )
        if guid is None or guid.strip() == "":
            raise AIHeroException(
                "You need to provide the guid to teach the automation with."
            )

        person["guid"] = guid
        return super()._sync_job({"type": "add_person_to_group_one", "row": person})

    def add_person_to_group_two(self, person, guid):
        if person is None or len(person) == 0:
            raise AIHeroException(
                "You need to provide the image to teach the automation with."
            )
        if guid is None or guid.strip() == "":
            raise AIHeroException(
                "You need to provide the guid to teach the automation with."
            )

        person["guid"] = guid
        return super()._sync_job({"type": "add_person_to_group_two", "row": person})

    def get_recommendations(self, person_id):
        if person_id is None or person_id.strip() == "":
            raise AIHeroException("person_id cannot be null or empty.")
        return super()._infer("get_recommendations", {"thing_id": person_id})
