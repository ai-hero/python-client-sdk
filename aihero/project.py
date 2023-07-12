from .client import Client
from .promptstash import PromptTemplate


class Project:
    """Main sync client class to talk to AI Hero"""

    def __init__(self, project_id: str, api_key: str, server_url: str = None):
        self._project_id = project_id
        self._client = Client(bearer_token=api_key, server_url=server_url)
        self.get()  # check

    def get(self, verbose: bool = False):
        project_dict = self._client.get(
            f"/workspace/projects/{self._project_id}",
            error_msg=f"Could fetch project details for project {self._project_id}",
            network_errors={
                400: "Please check the project_id.",
                403: f"Could not get project {self._project_id}. Please check the API key.",
            },
        )
        if verbose:
            print(f"Project id:\t{project_dict['project_id']}")
            print(f"Project name:\t{project_dict['name']}")
            print(f"Project desc:\t{project_dict['description']}")
            print(f"Created on:\t{project_dict['created_at']}")

    def prompt_template(self, prompt_template_id: str):
        return PromptTemplate(self._project_id, self._client, prompt_template_id)
