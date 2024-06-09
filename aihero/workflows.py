"""Project class to interact with AI Hero API"""
from .base_client import BaseClient
import time


class Workflow:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, project_id: str, workflow_id: str, base_client: BaseClient):
        self._project_id = project_id
        self._workflow_id = workflow_id
        self._base_client = base_client
        self.get()
        assert self._dict

    def get(self, verbose: bool = False):
        """Get project details"""
        self._dict = self._base_client.get(
            f"/projects/{self._project_id}/autonomous/workflows/{self._workflow_id}",
            error_msg=f"Could fetch project details for workflow {self._workflow_id}",
            network_errors={
                400: "Please check the workflow_id.",
                403: f"Could not get workflow {self._workflow_id}. Please check the API key.",
                404: "Could not find the workflow.",
            },
        )
        if verbose:
            print(f"Project id:\t{self._dict['project_id']}")
            print(f"Workflow id:\t{self._dict['workflow_id']}")
            print(f"Workflow name:\t{self._dict['name']}")
            print(f"Workflow desc:\t{self._dict['description']}")
            print(f"Created on:\t{self._dict['created_at']}")

        return self._dict

    def launch(self, verbose: bool = False, timeout=60):
        """Launch the workflow"""
        self.get()
        if self._dict["status"] in ["running", "pending"]:
            raise ValueError("Workflow is already running.")
        first_step = self._dict["steps"][0]
        tic = time.perf_counter()
        self._base_client.post(
            f"/projects/{self._project_id}/autonomous/workflows/{self._workflow_id}/launch",
            obj={"step_id": first_step["step_id"]},
            error_msg=f"Could launch for workflow {self._workflow_id}",
            network_errors={
                400: "Please check the workflow_id.",
                403: f"Could not get workflow {self._workflow_id}. Please check the API key.",
                404: "Could not find the workflow.",
            },
        )

        while True:
            self.get()
            if verbose:
                print(
                    f"\tWorkflow {self._dict['workflow_id']} status:\t{self._dict['status']}"
                )
            if self._dict["status"] in ["running", "pending"]:
                time.sleep(1)
            else:
                break
            if time.perf_counter() - tic > timeout:
                raise TimeoutError(
                    "Timeout while waiting for the workflow to complete."
                )
