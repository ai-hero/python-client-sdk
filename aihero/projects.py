"""Project class to interact with AI Hero API"""
import validators
import os
from .base_client import BaseClient
import validators


class Project:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, project_id: str, api_key: str):
        assert project_id, "Please provide a project_id"
        assert validators.uuid(project_id), "project_id should be a valid UUID"
        assert api_key, "Please provide an api_key"
        assert isinstance(api_key, str), "api_key should be a string."
        self._project_id = project_id
        self._client = BaseClient(api_key=api_key)
        self.get()  # check

    def get(self, verbose: bool = False):
        """Get project details"""
        project_dict = self._client.get(
            f"/projects/{self._project_id}",
            error_msg=f"Could fetch project details for project {self._project_id}",
            network_errors={
                400: "Please check the project_id.",
                403: f"Could not get project {self._project_id}. Please check the API key.",
                404: "Could not find the project.",
            },
        )
        if verbose:
            print(f"Project id:\t{project_dict['project_id']}")
            print(f"Project name:\t{project_dict['name']}")
            print(f"Project desc:\t{project_dict['description']}")
            print(f"Created on:\t{project_dict['created_at']}")
