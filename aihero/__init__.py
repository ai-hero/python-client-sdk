from aihero.exceptions import AIHeroException
from .api import Api
from .exceptions import AIHeroException
from .automation import Automation
from .detect_sentiment import DetectSentiment


class Client:
    """Main sync client class to talk to AI Hero"""

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
        if automation_definition["type"] == "detect_sentiment":
            automation = DetectSentiment(
                automation_id=automation_id,
                api=Api(api_key=api_key, server_url=self._api.server_url),
            )
        return automation
