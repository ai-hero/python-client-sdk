from fire import Fire
import os
from aihero import Client
from dotenv import load_dotenv
from aihero.schema import Markdown, Instruction, ModeEnum, TypeEnum


def main():
    """Create and launch a 'Content Writing - Blog about the Astronomical Earth' workflow"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    project_id = os.environ.get("AI_HERO_PROJECT_ID")
    client = Client(api_key=os.environ.get("AI_HERO_API_KEY"))

    # Define the workflow
    workflow = client.create_workflow(
        project_id=project_id,
        name="Content Writing - Blog about the Astronomical Earth",
        description="Create a blog post about the astronomical aspects of Earth.",
        steps=[
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="# Blog about the Astronomical Earth",
                description="Title for the blog post.",
            ),
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Introduction",
                description="Introduction section header.",
            ),
            Instruction(
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Write an introduction about Earth's astronomical significance.",
                markdown="(This section will contain the introduction.)",
                description="Introduction to Earth's astronomical significance.",
            ),
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Earth's Position in the Solar System",
                description="Section header for Earth's position in the solar system.",
            ),
            Instruction(
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Discuss Earth's position in the solar system.",
                markdown="(This section will contain information about Earth's position in the solar system.)",
                description="Details about Earth's position in the solar system.",
            ),
            Markdown(
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Earth's Rotation",
                description="Section header for Earth's rotation.",
            ),
            Instruction(
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Explain how Earth's rotation and orbit affect life.",
                markdown="(This section will explain the effects of Earth's rotation and orbit.)",
                description="Explanation of how Earth's rotation and orbit affect life.",
            ),
        ],
    )

    print(f"Workflow id:\t{workflow.workflow_id}")
    client.launch_workflow(
        project_id=project_id, workflow_id=workflow.workflow_id, verbose=True
    )


if __name__ == "__main__":
    Fire(main)
