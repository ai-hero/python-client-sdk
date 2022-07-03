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
        if api_key is None or api_key.strip() == "":
            self._api_key = None  # Only works for ping for now.
        else:
            self._api_key = api_key
            self._authorization = f"Bearer {self._api_key}"
            self._headers["Authorization"] = self._authorization

        if server_url.endswith("/"):
            server_url = server_url[:-1]
        self.server_url = server_url or PRODUCTION_URL

    def ping_endpoint(self):
        return f"{self.server_url}/ping"

    def endpoint(self, *args):
        return f"{self.server_url}/api/{'/'.join(args)}"

    def get(self, path, error_msg=None, network_errors=None):
        with httpx.Client() as client:
            response = client.get(path, headers=self._headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if network_errors and exc.response.status_code in network_errors:
                raise AIHeroException(
                    f"{network_errors[exc.response.status_code]}",
                    status_code=exc.response.status_code,
                )
            elif exc.response.status_code:
                raise AIHeroException(error_msg, status_code=exc.response.status_code)
            else:
                raise AIHeroException(error_msg)
        return response.json()

    def post(self, path, obj, error_msg=None, network_errors=None):
        with httpx.Client() as client:
            response = client.post(path, json=obj, headers=self._headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if network_errors and exc.response.status_code in network_errors:
                raise AIHeroException(
                    f"{network_errors[exc.response.status_code]}",
                    status_code=exc.response.status_code,
                )
            elif exc.response.status_code:
                raise AIHeroException(error_msg, status_code=exc.response.status_code)
            else:
                raise AIHeroException(error_msg)
        return response.json()
