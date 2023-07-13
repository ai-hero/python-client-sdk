import httpx
from .exceptions import AIHeroException
import traceback


PRODUCTION_URL = "https://app.aihero.studio"
SANDBOX_URL = "https://sandbox.aihero.studio"


class Client:
    """Abstraction for http operations"""

    _base_url: str = None
    _authorization: str = None

    def __init__(self, bearer_token: str, server_url: str = PRODUCTION_URL):
        self._bearer_token = bearer_token
        self._authorization = f"Bearer {self._bearer_token}"
        self._base_url = server_url
        print(f"Connecting to {self._base_url}")
        if self._base_url.endswith("/"):
            self._base_url = self._base_url[:-1]
        self._base_url = f"{self._base_url}/api/v1"

    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._authorization,
        }
        return headers

    def get(
        self,
        path: str,
        error_msg: str = None,
        network_errors: dict = None,
        timeout: int = 30,
    ) -> dict:
        with httpx.Client(base_url=self._base_url, timeout=timeout) as client:
            response = client.get(path, headers=self._get_headers())
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                msg = ""
                if network_errors and exc.response.status_code in network_errors:
                    raise AIHeroException(
                        f"{error_msg}: {network_errors[exc.response.status_code]} - {exc.response.text}",
                        status_code=exc.response.status_code,
                    ) from exc
                elif exc.response.status_code:
                    raise AIHeroException(
                        error_msg + "-" + exc.response.text,
                        status_code=exc.response.status_code,
                    ) from exc
                else:
                    msg = error_msg
                raise AIHeroException(msg) from exc
            return response.json()

    def post(
        self,
        path: str,
        obj: dict,
        error_msg: str = "Error",
        network_errors: dict = None,
        timeout: int = 30,
    ) -> dict:
        with httpx.Client(base_url=self._base_url, timeout=timeout) as client:
            response = client.post(path, json=obj, headers=self._get_headers())
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            msg = ""
            if network_errors and exc.response.status_code in network_errors:
                raise AIHeroException(
                    f"{error_msg}: {network_errors[exc.response.status_code]} - {exc.response.text}",
                    status_code=exc.response.status_code,
                ) from exc
            elif exc.response.status_code:
                raise AIHeroException(
                    error_msg + "-" + exc.response.text,
                    status_code=exc.response.status_code,
                ) from exc
            else:
                msg = error_msg
            raise AIHeroException(msg) from exc
        return response.json()
