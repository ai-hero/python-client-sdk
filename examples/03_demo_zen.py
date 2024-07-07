from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv
from aihero.schema import Markdown, Instruction, ModeEnum, TypeEnum


def main():
    """Check Existing Projects and Workflows"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    project_id = os.environ.get("AI_HERO_PROJECT_ID")
    client = Client(
        api_key=os.environ.get("AI_HERO_API_KEY"),
    )

    # Define the workflow
    workflow = client.create_workflow(
        project_id=project_id,
        name="Daily Moment of Zen",
        description="Start your day with a moment of zen.",
        steps=[
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="# Your Daily Moment of Zen",
                description="Begin your day with a calming message.",
            ),
            Instruction(
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Provide a calming message to start the day.",
                markdown="(This section will contain a calming message.)",
                description="Provide a calming message.",
            ),
        ],
    )

    print(f"Workflow id:\t{workflow.workflow_id}")
    client.launch_workflow(
        project_id=project_id,
        workflow_id=workflow.workflow_id,
        verbose=True,
    )


if __name__ == "__main__":
    Fire(main)
