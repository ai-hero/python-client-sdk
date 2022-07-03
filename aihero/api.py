import platform
import httpx
import urllib.parse

from .exceptions import AIHeroException

PRODUCTION_URL = "https://api.aihero.studio/"


class Api:
    """Abstraction for http operations"""

    def __init__(self, api_key, server_url=None):
        if api_key == "" or api_key is None:
            raise AIHeroException("Please provide a valid API Key.")
        self.api_key = api_key

        self._authorization = f"Bearer {self.api_key}"
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": self._authorization,
        }
        self._server_url = server_url or PRODUCTION_URL

    def endpoint(*args):
        self = args[0]
        return f"{self._server_url}/{'/'.join(args[1:])}"

    def get(self, path, error_msg=None):
        with httpx.Client() as client:
            response = client.get(path)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AIHeroException(
                f"Error {error_msg or path}", status_code=exc.response.status_code
            )
        return response.json()
