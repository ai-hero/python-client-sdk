from .project import Project


def promptstash(
    project_id: str, api_key: str, server_url: str = "https://app.aihero.studio"
):
    return Project(
        project_id=project_id, api_key=api_key, server_url=server_url
    ).promptstash()
