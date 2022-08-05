import httpx
from .exceptions import AIHeroException

PRODUCTION_URL = "https://api.aihero.studio"


class Api:
    """Abstraction for http operations"""

    def __init__(
        self, auth_secret: str = None, api_key: str = None, server_url: str = None
    ):
        if auth_secret is None or auth_secret.strip() == "":
            self._auth_secret = None  # Only works for ping for now.
        else:
            self._auth_secret = auth_secret
            self._auth_secret_authorization = f"Bearer {self._auth_secret}"

        if api_key is None or api_key.strip() == "":
            self._api_key = None  # Only works for ping for now.
        else:
            self._api_key = api_key
            self._api_key_authorization = f"Bearer {self._api_key}"

        if server_url.endswith("/"):
            server_url = server_url[:-1]
        self.server_url = server_url or PRODUCTION_URL

    def _get_headers(self, path: str) -> dict:
        headers = {
            "Content-Type": "application/json",
        }
        if "/workspace/" in path:
            # Prioritize workspace auth_key
            headers["Authorization"] = self._auth_secret_authorization
        elif "/automations/" in path:
            # api_key for automation
            headers["Authorization"] = self._api_key_authorization
        return headers

    def ping_endpoint(self) -> str:
        return f"{self.server_url}/ping"

    def endpoint(self, *args) -> str:
        return f"{self.server_url}/api/{'/'.join(args)}"

    def get(
        self, path: str, error_msg: str = None, network_errors: dict = None
    ) -> dict:
        with httpx.Client() as client:
            response = client.get(path, headers=self._get_headers(path), timeout=10.0)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if network_errors and exc.response.status_code in network_errors:
                raise AIHeroException(
                    f"{network_errors[exc.response.status_code]}",
                    status_code=exc.response.status_code,
                ) from exc
            elif exc.response.status_code:
                raise AIHeroException(
                    error_msg, status_code=exc.response.status_code
                ) from exc
            else:
                raise AIHeroException(error_msg) from exc
        return response.json()

    def post(
        self, path: str, obj: dict, error_msg: str = None, network_errors: dict = None
    ) -> dict:
        with httpx.Client() as client:
            response = client.post(
                path, json=obj, headers=self._get_headers(path), timeout=10.0
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if network_errors and exc.response.status_code in network_errors:
                raise AIHeroException(
                    f"{network_errors[exc.response.status_code]}",
                    status_code=exc.response.status_code,
                ) from exc
            elif exc.response.status_code:
                raise AIHeroException(
                    error_msg, status_code=exc.response.status_code
                ) from exc
            else:
                raise AIHeroException(error_msg) from exc
        return response.json()
