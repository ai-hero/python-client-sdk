"""aihero is a Python library for interacting with the aihero.studio API."""
from .project import Project

PRODUCTION_URL = "https://app.aihero.studio"


def promptstash(project_id: str, api_key: str, server_url: str = PRODUCTION_URL):
    """Returns a promptstash object to interact with promptstash."""
    return Project(
        project_id=project_id, api_key=api_key, server_url=server_url
    ).promptstash()
