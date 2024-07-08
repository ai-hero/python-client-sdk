from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv
from aihero.schema import Markdown, Instruction, Webpages, ModeEnum, TypeEnum


def main():
    """Create and launch a 'Analyzing Webpages - Summarizing TechCrunch Startups' workflow"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    project_id = os.environ.get("AI_HERO_PROJECT_ID")
    client = Client(api_key=os.environ.get("AI_HERO_API_KEY"))

    # Define the workflow
    workflow = client.create_workflow(
        project_id=project_id,
        name="Analyzing Webpages - Summarizing TechCrunch Startups",
        description="Summarize the latest articles about startups from TechCrunch.",
        steps=[
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="# Summary of TechCrunch Startups",
                description="Title for the summary.",
            ),
            Webpages(
                type=TypeEnum.WEBPAGES,
                mode=ModeEnum.EXPECTS,
                urls=["https://techcrunch.com/startups"],
                description="Analyze the latest articles from TechCrunch Startups.",
            ),
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Latest Articles from TechCrunch Startups",
                description="Section header for the summary.",
            ),
            Instruction(
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Summarize the main points from the latest TechCrunch articles about startups.",
                markdown="(This section will contain the summary.)",
                description="Summary of the main points from the latest TechCrunch articles.",
            ),
        ],
    )

    print(f"Workflow id:\t{workflow.workflow_id}")
    client.launch_workflow(
        project_id=project_id, workflow_id=workflow.workflow_id, verbose=True
    )


if __name__ == "__main__":
    Fire(main)
