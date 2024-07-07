from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv


def main():
    """Launch Existing Workflow"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    api_key = os.environ.get("AI_HERO_API_KEY")
    project_id = os.environ.get("AI_HERO_PROJECT_ID")
    client = Client(api_key=api_key)

    workflow_id = "aad492ad-b04f-4557-9070-fb56e00c2115"
    workflow = client.get_workflow(
        project_id=project_id,
        workflow_id=workflow_id,
    )
    print(f"Workflow id:\t{workflow.workflow_id}")
    print(f"Workflow name:\t{workflow.name}")
    print(f"Workflow desc:\t{workflow.description}")
    print(f"Created on:\t{workflow.created_at}")

    workflow = client.launch_workflow(
        project_id=project_id,
        workflow_id=workflow_id,
        verbose=True,
    )

    print("\n\nNVIDIA 10-Q Summary:")
    print(workflow.steps[-1].markdown)


if __name__ == "__main__":
    Fire(main)
