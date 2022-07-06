from .automation import Automation
from .exceptions import AIHeroException


class TagEntireImages(Automation):
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
                "type": "ingest_row",
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
