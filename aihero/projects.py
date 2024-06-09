"""Project class to interact with AI Hero API"""
import validators
import os
from .base_client import BaseClient
import validators


class Project:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, project_id: str, base_client: BaseClient):
        self._project_id = project_id
        self._base_client = base_client
        self.get()
        assert self._dict

    def get(self, verbose: bool = False):
        """Get project details"""
        self._dict = self._base_client.get(
            f"/projects/{self._project_id}",
            error_msg=f"Could fetch project details for project {self._project_id}",
            network_errors={
                400: "Please check the project_id.",
                403: f"Could not get project {self._project_id}. Please check the API key.",
                404: "Could not find the project.",
            },
        )
        if verbose:
            print(f"Project id:\t{self._dict['project_id']}")
            print(f"Project name:\t{self._dict['name']}")
            print(f"Project desc:\t{self._dict['description']}")
            print(f"Created on:\t{self._dict['created_at']}")

        return self._dict

    def list_workflows(self, verbose: bool = False):
        """List all workflows in the project"""
        workflows_list = self._base_client.get(
            f"/projects/{self._project_id}/autonomous/workflows"
        )["workflows"]
        if verbose:
            for workflow in workflows_list:
                print(f"Workflow id:\t{workflow['workflow_id']}")
                print(f"\tWorkflow name:\t{workflow['name']}")
                print(f"\tWorkflow desc:\t{workflow['description']}")
                print(f"\tCreated on:\t{workflow['created_at']}")
