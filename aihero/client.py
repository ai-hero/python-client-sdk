"""Client for AI Hero API"""

from warnings import warn
import os
import httpx
from typing import Optional, List, Dict
from .exceptions import AIHeroException
import validators
import traceback
from .schema import Project, Workflow, Step
import time
from pathlib import Path
from typing import Any

PRODUCTION_URL = "https://app.aihero.studio/"
STAGING_URL = "https://staging.aihero.studio/"


class Client:
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

    def _get_headers(self) -> Any:
        """Get headers for http requests"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._authorization,
        }
        return headers

    def __validate_inputs(
        self,
        path: str,
        error_msg: str,
        network_errors: Optional[Dict[int, str]],
        timeout: int,
    ) -> None:
        """Validate the inputs for the __put_bytes method."""
        if not path:
            raise ValueError("Please provide a path")
        if not isinstance(path, str):
            raise ValueError("path should be a string.")
        if not error_msg:
            raise ValueError("Please provide an error_msg")
        if not isinstance(error_msg, str):
            raise ValueError("error_msg should be a string.")
        if not network_errors:
            network_errors = {}
        if not isinstance(network_errors, dict):
            raise ValueError("network_errors should be a dict.")
        for k, v in network_errors.items():
            if not isinstance(k, int):
                raise ValueError(
                    f"key {k} in network_errors should be an integer HTTP status code."
                )
            if not isinstance(v, str):
                raise ValueError(f"message {v} in network_errors should be a string.")
        if not timeout:
            raise ValueError("Please provide a timeout")
        if not isinstance(timeout, int):
            raise ValueError("timeout should be an int.")
        if not path.startswith("/"):
            raise ValueError("path should start with '/'")
        if not validators.url(f"{self._base_url}{path}"):
            raise ValueError(f"Invalid path '{path}'")

    def __get(
        self,
        path: str,
        error_msg: str = "Error",
        network_errors: Optional[dict[int, str]] = None,
        timeout: int = 30,
    ) -> Any:
        """Get request to AI Hero server"""
        if not network_errors:
            network_errors = {}

        # Validate inputs
        self.__validate_inputs(path, error_msg, network_errors, timeout)

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

    def __post(
        self,
        path: str,
        obj: dict[str, Any],
        error_msg: str = "Error",
        network_errors: Optional[dict[int, str]] = None,
        timeout: int = 30,
    ) -> Any:
        """Post request to AI Hero server"""
        if not network_errors:
            network_errors = {}
        # Validate inputs
        self.__validate_inputs(path, error_msg, network_errors, timeout)

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

    def __put_bytes(
        self,
        path: str,
        content: bytes,
        error_msg: str = "Error",
        network_errors: Optional[Dict[int, str]] = None,
        timeout: int = 30,
    ) -> None:
        """Post request to AI Hero server"""
        if not network_errors:
            network_errors = {}
        # Validate inputs
        self.__validate_inputs(path, error_msg, network_errors, timeout)

        # HTTP request
        with httpx.Client(base_url=self._base_url, timeout=timeout) as client:
            response = client.put(path, data=content, headers=self._get_headers())

        # Response handling
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            msg = network_errors.get(status_code, f"{error_msg} - {exc.response.text}")
            raise AIHeroException(msg, status_code=status_code) from exc

    def get_project(self, project_id: str) -> Project:
        """Get project details"""
        obj = self.__get(
            f"/projects/{project_id}",
            error_msg=f"Could fetch project details for project {project_id}",
            network_errors={
                400: "Please check the project_id.",
                403: f"Could not get project {project_id}. Please check the API key.",
                404: "Could not find the project.",
            },
        )
        project = Project.from_dict(obj)
        return project

    def list_workflows(self, project_id: str) -> list[Workflow]:
        """List all workflows in the project"""
        workflows_list = self.__get(f"/projects/{project_id}/autonomous/workflows")[
            "workflows"
        ]
        return [Workflow.from_dict(workflow) for workflow in workflows_list]

    def get_workflow(
        self, project_id: str, workflow_id: str, verbose: bool = False
    ) -> Workflow:
        """Get project details"""
        obj = self.__get(
            f"/projects/{project_id}/autonomous/workflows/{workflow_id}",
            error_msg=f"Could fetch project details for workflow {workflow_id}",
            network_errors={
                400: "Please check the workflow_id.",
                403: f"Could not get workflow {workflow_id}. Please check the API key.",
                404: "Could not find the workflow.",
            },
        )
        return Workflow.from_dict(obj)

    def launch_workflow(
        self,
        project_id: str,
        workflow_id: str,
        verbose: bool = False,
        timeout: int = 60,
    ) -> Workflow:
        """Launch the workflow"""
        tic = time.perf_counter()
        workflow = self.get_workflow(project_id, workflow_id)
        first_step = workflow.steps[0]
        self.__post(
            f"/projects/{project_id}/autonomous/workflows/{workflow_id}/launch",
            obj={"step_id": first_step.step_id},
            error_msg=f"Could launch for workflow {workflow_id}",
            network_errors={
                400: "Please check the workflow_id.",
                403: f"Could not get workflow {workflow_id}. Please check the API key.",
                404: "Could not find the workflow.",
            },
        )

        while True:
            workflow = self.get_workflow(project_id, workflow_id)
            if verbose:
                print(
                    f"\tWorkflow {workflow_id} status:\t{workflow.status} at {workflow.updated_at}"
                )
            if workflow.status in ["running", "pending"]:
                time.sleep(1)
            else:
                break
            if time.perf_counter() - tic > timeout:
                raise TimeoutError(
                    "Timeout while waiting for the workflow to complete."
                )
        return workflow

    def create_workflow(
        self, project_id: str, name: str, description: str, steps: List[Step]
    ) -> Workflow:
        """Save the workflow"""
        obj = self.__post(
            f"/projects/{project_id}/autonomous/workflows",
            obj={
                "name": name,
                "kind": "simple",
                "description": description,
                "steps": [step.model_dump() for step in steps],
            },
            error_msg="Could not create a workflow",
            network_errors={
                400: "Could not create the workflow. ",
                403: "Could not create. Please check the API key.",
                404: "Could not find the workflow.",
            },
        )
        return Workflow.from_dict(obj)

    def upload_file(self, project_id: str, file: Path) -> None:
        """Upload a file to the project"""
        # Read the file content
        with open(file, "rb") as f:
            file_content = f.read()

        self.__put_bytes(
            f"/v1/projects/{project_id}/files/uploads/{file.name}",
            file_content,
            error_msg="Could not upload the file",
            network_errors={
                400: "Could not upload the file. ",
                403: f"Could not upload the file {file}. Please check the API key.",
                404: "Could not upload the file.",
            },
        )
