from .automation import Automation
from .exceptions import AIHeroException


class DetectSentiment(Automation):
    def predict(self, text):
        if text is None or text.strip() == "":
            raise AIHeroException("text cannot be null or empty.")
        return super().predict({"text": text})
