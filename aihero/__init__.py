"""aihero is a Python library for interacting with the aihero.studio API."""
from .projects import Project
from .base_client import BaseClient
from .workflows import Workflow


class Client:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, api_key: str):
        self._client = BaseClient(api_key)

    def get_project(self, project_id: str) -> Project:
        """Get project details"""
        return Project(project_id=project_id, base_client=self._client)

    def get_workflow(self, project_id: str, workflow_id: str) -> Workflow:
        """Get workflow details"""
        return Workflow(
            project_id=project_id, workflow_id=workflow_id, base_client=self._client
        )
