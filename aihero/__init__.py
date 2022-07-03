from aihero.exceptions import AIHeroException
from .api import Api
from .exceptions import AIHeroException


class Client:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, api_key=None, server_url=None):
        self._server_url = server_url
        self._api = Api(api_key=api_key, server_url=server_url)

    def ping(self):
        return self._api.get(
            self._api.ping_endpoint(),
            error_msg=f"Could not connect to the server {self._server_url}",
        )
