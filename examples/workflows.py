from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv


def main():
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    api_key = os.environ.get("AI_HERO_API_KEY")
    project_id = os.environ.get("AI_HERO_PROJECT_ID")
    client = Client(api_key=api_key)
    project = client.get_project(project_id=project_id)

    project.list_workflows()

    workflow_id = "57662519-dd45-4175-88cf-a23fe6a55b11"
    workflow = client.get_workflow(project_id=project_id, workflow_id=workflow_id)

    workflow.launch(verbose=True)

    print(workflow.get()["steps"][-1]["text"])


if __name__ == "__main__":
    Fire(main)
