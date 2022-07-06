from .automation import Automation
from .exceptions import AIHeroException


class DetectSentiment(Automation):
    def add(self, text, guid):
        if text is None or text.strip() == "":
            raise AIHeroException(
                "You need to provide the text to teach the automation with."
            )
        if guid is None or guid.strip() == "":
            raise AIHeroException(
                "You need to provide the guid to teach the automation with."
            )

        return super()._sync_job(
            {"type": "ingest_row", "row": {"text": text, "guid": guid}}
        )

    def predict(self, text):
        if text is None or text.strip() == "":
            raise AIHeroException("text cannot be null or empty.")
        return super()._infer("predict", {"text": text})
