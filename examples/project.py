from fire import Fire
import os
from aihero import Project
from dotenv import load_dotenv


def main():
    load_dotenv()
    assert os.environ.get("AI_HERO_PROJECT_ID"), "Please provide an AI_HERO_PROJECT_ID"
    assert os.environ.get(
        "AI_HERO_PROJECT_API_KEY"
    ), "Please provide an AI_HERO_PROJECT_API_KEY"
    project = Project(
        project_id=os.environ.get("AI_HERO_PROJECT_ID"),
        api_key=os.environ.get("AI_HERO_PROJECT_API_KEY"),
    )
    print(project.get(verbose=True))


if __name__ == "__main__":
    Fire(main)
