from fire import Fire
import os
from pathlib import Path
from uuid import uuid4
from aihero import Client
from dotenv import load_dotenv
from aihero.schema import Markdown, Files, Instruction, ModeEnum, TypeEnum


def main() -> None:
    """Create and launch a 'Analyzing Files - Analyze a 10-k Filing for ESG' workflow"""
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get("AI_HERO_API_KEY"), "Please provide an AI_HERO_API_KEY"
    project_id = os.environ["AI_HERO_PROJECT_ID"]
    client = Client(api_key=os.environ["AI_HERO_API_KEY"])

    filename = "tsla-20231231-gen.pdf"
    file = Path(__file__).parent / "data" / filename
    assert os.path.exists(file), f"File not found: {file}"
    client.upload_file(project_id=project_id, file=file)

    # Define the workflow
    workflow = client.create_workflow(
        project_id=project_id,
        name="Analyzing Files - Analyze a 10-k Filing for ESG",
        description="Upload a 10-k filing and extract ESG information.",
        steps=[
            Markdown(
                step_id=str(uuid4()),
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="# Analyze a 10-k Filing for ESG",
                description="Workflow to analyze a 10-k filing.",
                error="",
            ),
            Files(
                step_id=str(uuid4()),
                type=TypeEnum.FILES,
                mode=ModeEnum.EXPECTS,
                files=[filename],
                description="Upload the latest 10-k filing of the company.",
                processed_files={},
                metadata_files={},
                error="",
            ),
            Markdown(
                step_id=str(uuid4()),
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Analysis of Environmental Initiatives",
                description="Section header for ESG analysis.",
                error="",
            ),
            Instruction(
                step_id=str(uuid4()),
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Analyze the environmental initiatives mentioned in the 10-k filing.",
                markdown="(This section will contain the analysis of environmental initiatives.)",
                description="Analysis of environmental initiatives.",
                error="",
            ),
            Markdown(
                step_id=str(uuid4()),
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Analysis of Social Initiatives",
                description="Section header for ESG analysis.",
                error="",
            ),
            Instruction(
                step_id=str(uuid4()),
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Analyze the social initiatives mentioned in the 10-k filing.",
                markdown="(This section will contain the analysis of social initiatives.)",
                description="Analysis of social initiatives.",
                error="",
            ),
            Markdown(
                step_id=str(uuid4()),
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Analysis of Governance Initiatives",
                description="Section header for ESG analysis.",
            ),
            Instruction(
                step_id=str(uuid4()),
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Analyze the governance initiatives mentioned in the 10-k filing.",
                markdown="(This section will contain the analysis of governance initiatives.)",
                description="Analysis of governance initiatives.",
            ),
            Markdown(
                step_id=str(uuid4()),
                type=TypeEnum.MARKDOWN,
                mode=ModeEnum.OUTPUT,
                markdown="## Summary of ESG Analysis",
                description="Section header for ESG analysis.",
            ),
            Instruction(
                step_id=str(uuid4()),
                type=TypeEnum.INSTRUCTION,
                mode=ModeEnum.OUTPUT,
                instruction="Provide a summary of the ESG analysis.",
                markdown="(This section will contain the summary of the ESG analysis.)",
                description="Summary of the ESG analysis.",
            ),
        ],
    )

    print(f"Workflow id:\t{workflow.workflow_id}")
    client.launch_workflow(
        project_id=project_id, workflow_id=workflow.workflow_id, verbose=True
    )


if __name__ == "__main__":
    Fire(main)
