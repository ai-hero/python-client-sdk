import os
import fire
import subprocess


def pe(app: str = "completions"):
    # Get the current directory of cli.py
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the Streamlit app
    app_path = os.path.join(current_dir, "apps", f"{app}.py")

    # Run the Streamlit app using subprocess
    command = f"streamlit run {app_path}"
    subprocess.run(command, shell=True, check=True)


def main():
    # Using Fire to automatically generate a command line interface
    fire.Fire(
        {
            "pe": pe,
            # Add more commands as needed
        }
    )


if __name__ == "__main__":
    main()
