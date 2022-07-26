from .automation import Automation, COLORS


class TagEntireImages(Automation):
    def get_tags(self) -> list[str]:
        automation_definition = super().get_definition()
        ontology = automation_definition.get("ontology", [])
        return [c["name"] for c in ontology]

    def set_tags(self, tags: list[str]) -> list[str]:
        assert tags is not None
        assert len(tags) > 0
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

    def add_image(self, guid: str, image_url: str) -> dict:
        assert image_url is not None
        assert guid is not None

        return super()._sync_job(
            {
                "type": "add_image",
                "row": {
                    "image": {"type": "url_pointer", "url": image_url},
                    "guid": guid,
                },
            }
        )

    def predict(self, guid: str, image_url: str) -> dict:
        assert image_url is not None
        assert guid is not None
        return super()._infer(
            "predict",
            {"image": {"type": "url_pointer", "url": image_url}, "guid": guid},
        )

    def set_ground_truth(self, guid: str, ground_truth: dict[str, bool]) -> dict:
        assert guid is not None
        return super()._sync_job(
            {
                "type": "set_ground_truth",
                "guid": guid,
                "ground_truth": ground_truth,
            }
        )
