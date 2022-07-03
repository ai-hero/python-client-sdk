from .automation import Automation
from .exceptions import AIHeroException


class TagEntireImages(Automation):
    def predict(self, image_url=None):
        if image_url is None or image_url.strip() == "":
            raise AIHeroException("image_url cannot be null or empty.")
        return super().infer("predict", {"image": image_url})
