from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv


def main():
    """Check Existing Projects and Workflows"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    client = Client(
        api_key=os.environ.get("AI_HERO_API_KEY"),
    )
    project = client.get_project(os.environ.get("AI_HERO_PROJECT_ID"))
    print(f"Project id:\t{project.project_id}")
    print(f"Project name:\t{project.name}")
    print(f"Project desc:\t{project.description}")
    print(f"Created on:\t{project.created_at}")

    workflows = client.list_workflows(
        project_id=os.environ.get("AI_HERO_PROJECT_ID"),
    )
    for workflow in workflows:
        print(f"Workflow id:\t{workflow.workflow_id}")
        print(f"\tWorkflow name:\t{workflow.name}")
        print(f"\tWorkflow desc:\t{workflow.description}")
        print(f"\tCreated on:\t{workflow.created_at}")


if __name__ == "__main__":
    Fire(main)
