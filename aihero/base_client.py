"""Client for AI Hero API"""
from warnings import warn
import os
import httpx
from typing import Any, Optional
from .exceptions import AIHeroException
import validators
import traceback

PRODUCTION_URL = "https://app.aihero.studio/"
STAGING_URL = "https://staging.aihero.studio/"


class BaseClient:
    """Abstraction for http operations"""

    _base_url: Optional[str] = None
    _authorization: Optional[str] = None

    def __init__(self, api_key: str):
        server_url = os.environ.get("AI_HERO_SERVER_URL", PRODUCTION_URL)
        assert api_key, "Please provide an api_key"
        assert isinstance(api_key, str), "api_key should be a string."
        assert server_url, "Please provide a server_url"
        assert server_url in [
            STAGING_URL,
            PRODUCTION_URL,
        ], f"Server URL should be {PRODUCTION_URL}"
        self._api_key = api_key

        # Assign to self
        self._authorization = f"Bearer {self._api_key}"
        self._base_url = server_url

        if server_url != PRODUCTION_URL:
            warn(f"Connecting to {self._base_url}")
        if self._base_url.endswith("/"):
            self._base_url = self._base_url[:-1]
        self._base_url = f"{self._base_url}/api/v1"

    def _get_headers(self) -> dict:
        """Get headers for http requests"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._authorization,
        }
        return headers

    def get(
        self,
        path: str,
        error_msg: str = "Error",
        network_errors: Optional[dict[int, str]] = None,
        timeout: int = 30,
    ) -> dict:
        """Get request to AI Hero server"""
        assert path, "Please provide a path"
        assert isinstance(path, str), "path should be a string."
        assert error_msg, "Please provide an error_msg"
        assert isinstance(error_msg, str), "error_msg should be a string."
        if not network_errors:
            network_errors = {}
        assert isinstance(network_errors, dict), "network_errors should be a dict."
        for k, v in network_errors.items():  # pylint: disable=invalid-name
            assert isinstance(
                k, int
            ), f"key {k} in network_errors should be an integer HTTP status code."
            assert isinstance(
                v, str
            ), f"message {v} in network_errors should be a string."
        assert timeout, "Please provide a timeout"
        assert isinstance(timeout, int), "timeout should be a int."
        assert path.startswith("/"), "path should start with '/'"
        assert validators.url(f"{self._base_url}{path}"), f"Invalid path '{path}'"

        with httpx.Client(base_url=self._base_url, timeout=timeout) as client:
            try:
                response = client.get(path, headers=self._get_headers())
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                traceback.print_exc()
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
        network_errors: Optional[dict[int, str]] = None,
        timeout: int = 30,
    ) -> dict:
        """Post request to AI Hero server"""
        assert path, "Please provide a path"
        assert isinstance(path, str), "path should be a string."
        assert error_msg, "Please provide an error_msg"
        assert isinstance(error_msg, str), "error_msg should be a string."
        if not network_errors:
            network_errors = {}
        assert isinstance(network_errors, dict), "network_errors should be a dict."
        for k, v in network_errors.items():  # pylint: disable=invalid-name
            assert isinstance(
                k, int
            ), f"key {k} in network_errors should be an integer HTTP status code."
            assert isinstance(
                v, str
            ), f"message {v} in network_errors should be a string."
        assert timeout, "Please provide a timeout"
        assert isinstance(timeout, int), "timeout should be a int."
        assert path.startswith("/"), "path should start with '/'"
        assert validators.url(f"{self._base_url}{path}"), f"Invalid path '{path}'"

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
