import platform
import httpx
import urllib.parse

from .exceptions import AIHeroException

PRODUCTION_URL = "https://api.aihero.studio"


class Api:
    """Abstraction for http operations"""

    def __init__(self, api_key=None, server_url=None):
        self._headers = {
            "Content-Type": "application/json",
        }
        if api_key == "" or api_key is None:
            self._api_key = None  # Only works for ping for now.
        else:
            self._api_key = api_key
            self._authorization = f"Bearer {self._api_key}"
            self._headers["Authorization"] = self._authorization

        self._server_url = server_url or PRODUCTION_URL

    def ping_endpoint(self, *args):
        return f"{self._server_url}/{'/'.join(args)}"

    def endpoint(self, *args):
        return f"{self._server_url}/api/{'/'.join(args)}"

    def get(self, path, error_msg=None):
        with httpx.Client() as client:
            response = client.get(path, headers=self._headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AIHeroException(
                f"Error {error_msg or path}", status_code=exc.response.status_code
            )
        return response.json()
