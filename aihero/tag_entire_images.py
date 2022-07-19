from .automation import Automation, COLORS
from .exceptions import AIHeroException


class TagEntireImages(Automation):
    def get_tags(self):
        automation_definition = super().get_definition()
        ontology = automation_definition.get("ontology", [])
        return [c["name"] for c in ontology]

    def set_tags(self, tags):
        automation_definition = super().get_definition()
        ontology = []
        existing_in_ontology = []
        colors_to_select_from = [c for c in COLORS]

        for c in automation_definition.get("ontology", []):
            if c not in tags:
                continue  # Remove tags no longer needed
            ontology.append(c)
            existing_in_ontology.append(c["name"])
            colors_to_select_from.remove(c["color"])

        for t in tags:
            if t not in existing_in_ontology:
                ontology.append(
                    {
                        "type": "class",
                        "_id": t,
                        "name": t,
                        "color": colors_to_select_from.pop(),
                    }
                )

        super().update_ontology(ontology)
        return self.get_tags()

    def add(self, image_url, guid):
        if image_url is None or image_url.strip() == "":
            raise AIHeroException(
                "You need to provide the image to teach the automation with."
            )
        if guid is None or guid.strip() == "":
            raise AIHeroException(
                "You need to provide the guid to teach the automation with."
            )

        return super()._sync_job(
            {
                "type": "add_image",
                "row": {
                    "image": {"type": "url_pointer", "url": image_url},
                    "guid": guid,
                },
            }
        )

    def predict(self, image_url=None):
        if image_url is None or image_url.strip() == "":
            raise AIHeroException("image_url cannot be null or empty.")
        return super()._infer(
            "predict", {"image": {"type": "url_pointer", "url": image_url}}
        )
