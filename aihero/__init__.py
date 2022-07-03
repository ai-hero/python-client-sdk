from aihero.exceptions import AIHeroException
from .api import Api
from .exceptions import AIHeroException
from .automation import Automation
from .detect_sentiment import DetectSentiment
from .tag_short_text import TagShortText
from .tag_entire_images import TagEntireImages
from .user_recommendation import UserRecommendation
from .item_recommendation import ItemRecommendation


class Client:
    """Main sync client class to talk to AI Hero"""

    automation_classes = {
        "detect_sentiment": DetectSentiment,
        "tag_short_text": TagShortText,
        "tag_entire_images": TagEntireImages,
        "item_recommendation": ItemRecommendation,
        "user_recommendation": UserRecommendation,
    }

    def __init__(self, api_key=None, server_url=None):
        self._api = Api(api_key=api_key, server_url=server_url)

    def ping(self):
        return self._api.get(
            self._api.ping_endpoint(),
            error_msg=f"Could not connect to the server {self._api.server_url}",
        )

    def get_automation(self, automation_id, api_key):
        automation = Automation(
            automation_id=automation_id,
            api=Api(api_key=api_key, server_url=self._api.server_url),
        )
        automation_definition = automation.get_definition()
        automation_type = automation_definition["type"]
        if automation_type not in Client.automation_classes:
            raise AIHeroException(
                f"Unsupported automation type for the API: {automation_type}"
            )
        automation_api = Api(api_key=api_key, server_url=self._api.server_url)
        automation = Client.automation_classes[automation_type](
            automation_id=automation_id, api=automation_api
        )
        return automation
