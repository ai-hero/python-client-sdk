import streamlit as st
import openai
import re
from dotenv import load_dotenv
import os
from aihero import promptstash
from uuid import uuid4
from datetime import date
import time
import pandas as pd
from aihero.eval import PromptTestSuite


# Construct the path to the .env file in the current working directory
env_path = os.path.join(os.getcwd(), ".env")

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Check for environment variables
if not os.path.exists(".env"):
    st.error(
        "Error: .env file is missing. Please ensure you have a .env file with the required keys."
    )
    st.write(
        "Get the necessary keys from [OpenAI](https://openai.com) or [AI Hero](https://app.aihero.studio)"
    )
    st.stop()

required_keys = ["OPENAI_API_KEY", "AI_HERO_PROJECT_ID", "AI_HERO_PROJECT_API_KEY"]

missing_keys = [key for key in required_keys if os.getenv(key) is None]

if missing_keys:
    st.error(f"Error: Missing keys in .env file: {', '.join(missing_keys)}")
    st.write(
        "Get the necessary keys from [OpenAI](https://openai.com) or [AI Hero](https://app.aihero.studio)"
    )
    st.stop()

openai.api_key = os.getenv("OPENAI_API_KEY")
AI_HERO_PROJECT_ID = os.getenv("AI_HERO_PROJECT_ID")
AI_HERO_PROJECT_API_KEY = os.getenv("AI_HERO_PROJECT_API_KEY")

ps = promptstash(project_id=AI_HERO_PROJECT_ID, api_key=AI_HERO_PROJECT_API_KEY)


# Set page layout to wide mode
st.set_page_config(layout="wide")


# Function to extract f-string variables
def extract_fstring_variables(template):
    return re.findall(r"\{(\w+)\}", template)


# CSS to expand the sidebar width
st.markdown(
    """
<style>
[data-testid="stSidebar"][role="complementary"] {
    width: 35%;
}
.css-pxxe24 {
visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)


# Streamlit App
def main():
    # Using Sidebar for Prompt Template and Settings
    st.sidebar.write("**Step 1: Prompt Template:**")

    st.session_state.template_id = st.sidebar.text_input(
        "Template ID:", "english-to-japanese", key="4"
    )

    if st.session_state.template_id:
        with st.sidebar.expander("Optional: Load an existing variant", expanded=False):
            # Text input for the variant appears once the button is pressed
            st.session_state.variant_to_load = st.text_input("Variant ID:", key="5")
            st.markdown(
                f"[All your existing variants `{st.session_state.template_id}`](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/prompt_templates/{st.session_state.template_id})"
            )

        # Load the template from the variant
        if st.session_state.variant_to_load:
            st.session_state.current_template = ps.variant(
                template_id=st.session_state.template_id,
                variant=st.session_state.variant_to_load,
            )
            st.session_state.current_variant = (
                st.session_state.variant_to_load
            )  # Update the session state variable with the loaded template
        else:
            st.session_state.current_variant = ""
            st.session_state.current_template = """Translate the following text into Japanese:\n{text}\n\nTranslation:"""

        st.sidebar.divider()
        st.sidebar.write("**Step 2: Enter a Prompt Template:**")

        st.session_state.template = st.sidebar.text_area(
            "Enter your f-string prompt template:",
            st.session_state.current_template,
            key="1",
            height=400,
        )

        st.sidebar.write(f"Current Template ID: {st.session_state.template_id}")

        if st.session_state.template:
            st.session_state.current_variant = ps.stash_template(
                template_id=st.session_state.template_id, body=st.session_state.template
            )
            # Right-aligned and smaller text for the prompt variant
            st.sidebar.markdown(
                f"Variant saved as [`{st.session_state.current_variant}`](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/prompt_templates/{st.session_state.template_id})"
            )

        st.sidebar.divider()

        # Advanced settings within a collapsible section in the sidebar
        with st.sidebar.expander("Settings", expanded=False):
            st.write("**Optional:**")
            st.write("**Advanced model and query settings:**")
            st.session_state.engine = st.text_input(
                "Model name:", "text-davinci-003", key="2"
            )
            st.session_state.temperature = st.text_input("Temperature:", "0.7", key="3")
            st.session_state.max_tokens = st.text_input("Max Tokens:", "256", key="6")
            st.session_state.model = {
                "name": st.session_state.engine,
                "engine": st.session_state.engine,
                "temperature": float(st.session_state.temperature),
                "max_tokens": int(st.session_state.max_tokens),
                "version": date.today().strftime("%Y-%m-%d"),
            }

    st.title("PromptCraft - Prompt Engineering using OpenAI Completions API.")
    st.text(
        "PromptCraft, by AI Hero, is the fastest way for product managers and prompt engineers \nto iterate on a prompt and share it with their engineering team."
    )
    if not st.session_state.template_id.strip():
        st.warning("Please enter a template ID in the sidebar on the left.")
    elif not st.session_state.template.strip():
        st.warning("Please enter your prompt template in the sidebar on the left.")
    else:
        with st.expander("Try it out", expanded=True):
            # Extract f-string variables and provide input boxes on the main area
            variables = extract_fstring_variables(st.session_state.template)
            st.session_state.user_inputs = {}
            for var in variables:
                st.session_state.user_inputs[var] = st.text_input(
                    f"Enter value for {var}",
                    key=f"input_{var}",
                )

            # Spacing
            st.text("")

            # Button to generate completion
            if st.button("Generate"):
                # Indicate process is running
                with st.spinner("Running..."):
                    trace_id = str(uuid4())
                    step_id = str(uuid4())
                    filled_template = st.session_state.template.format(
                        **st.session_state.user_inputs
                    )
                    prompt = filled_template
                    inputs = st.session_state.user_inputs
                    rendered_inputs = "\n".join(
                        [f"{k}: {v}" for k, v in inputs.items()]
                    )

                    # Capture the start time (tic) right before making the API call
                    tic = time.perf_counter()

                    # Get completion from OpenAI API
                    response = openai.Completion.create(
                        engine=st.session_state.engine,
                        prompt=filled_template,
                        temperature=float(st.session_state.temperature),
                        max_tokens=int(st.session_state.max_tokens),
                    )

                    # Capture the end time (toc) after getting the response
                    toc = time.perf_counter()

                    # Displaying the completion as text
                    st.markdown("**Result:**")
                    st.text("Inputs: ")
                    st.markdown(f"```{rendered_inputs}```")
                    st.text("Completion: ")
                    st.markdown(f"```{response.choices[0].text}```")

                    output = response.choices[0].text

                    ps.stash_completion(
                        trace_id=trace_id,
                        step_id=step_id,
                        template_id=st.session_state.template_id,
                        variant=st.session_state.current_variant,
                        prompt=prompt,
                        output=output,
                        inputs=inputs,
                        rendered_inputs=rendered_inputs,
                        model=st.session_state.model,
                        metrics={"time": (toc - tic)},
                        other={"usage": response.usage},
                    )

                    st.markdown(
                        f"You can see your trace saved with the trace_id `{trace_id}` [here](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/traces)"
                    )

        with st.expander("Evaluation", expanded=False):
            # Text area for Python code
            python_code = st.text_area(
                "Enter your Python code:",
                """class Tests(PromptTestSuite):
    # Pythonic test
    def test_has_length(self, output):        
        assert len(output)

    # Evaluate using gpt-3.5-turbo
    def ask_is_japanese(self) -> str:
        return "Does the text contain Japanese?"
        
    def test_has_pronunciation_guide(self, output):
        assert "pronunc" in output.lower() or "pronoun" in output.lower(), "The output doesn't contain a pronunciation guide."

    def ask_is_casual(self) -> str:
        return "Is the text in Japanese using a casual form (i.e. suitable for friends)?"
            """,
                height=400,
            )

            if "class Tests(PromptTestSuite)" not in python_code:
                st.warning(
                    "Please ensure your Python code contains a class named `Tests` that inherits from `PromptTestSuite`."
                )
                st.stop()

            try:
                exec(python_code, globals())  # pylint: disable=exec-used
                st.success("Code executed successfully!")
                test_template_id = f"{st.session_state.template_id}-test"

                test_suite = ps.build_test_suite(
                    test_suite_id=test_template_id, test_suite_cls=Tests
                )

                # Upload CSV file
                uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

                if uploaded_file:
                    data = pd.read_csv(uploaded_file)

                    # Check if all required columns exist in the uploaded CSV
                    missing_columns = [
                        var for var in variables if var not in data.columns
                    ]

                    if missing_columns:
                        st.error(
                            f"Uploaded CSV is missing the following columns: {', '.join(missing_columns)}"
                        )
                    else:
                        st.success("CSV file successfully uploaded and columns match!")

                        # Your provided code starts here
                        with st.spinner("Running..."):
                            completions = []
                            times = []
                            for index, row in data.iterrows():
                                # Update session state user_inputs for the current row
                                st.session_state.user_inputs = row.to_dict()

                                filled_template = st.session_state.template.format(
                                    **st.session_state.user_inputs
                                )
                                prompt = filled_template
                                inputs = st.session_state.user_inputs
                                rendered_inputs = "\n".join(
                                    [f"{k}: {v}" for k, v in inputs.items()]
                                )

                                # Capture the start time (tic) right before making the API call
                                tic = time.perf_counter()

                                # Get completion from OpenAI API
                                response = openai.Completion.create(
                                    engine=st.session_state.engine,
                                    prompt=filled_template,
                                    temperature=float(st.session_state.temperature),
                                    max_tokens=int(st.session_state.max_tokens),
                                )

                                # Capture the end time (toc) after getting the response
                                toc = time.perf_counter()

                                # Displaying the completion as text for each row
                                st.markdown(f"**Row {index + 1}:**")
                                st.text("Inputs: ")
                                st.markdown(f"```{rendered_inputs}```")
                                st.text("Completion: ")
                                st.markdown(f"```{response.choices[0].text}```")

                                output = response.choices[0].text
                                this_time = toc - tic

                                completions.append(
                                    {
                                        "inputs": inputs,
                                        "rendered_inputs": rendered_inputs,
                                        "prompt": prompt,
                                        "output": output,
                                    }
                                )
                                times.append(this_time)

                            # Next, we calculate the average time taken, and run the test suite on our test cases.
                            avg_time = sum(times) / len(times)

                            with st.spinner(
                                "Running Tests (please check your console for progress)..."
                            ):
                                test_run_id, summary = test_suite.run(
                                    template_id=st.session_state.template_id,
                                    variant=st.session_state.current_variant,
                                    completions=completions,
                                    model=st.session_state.model,
                                    metrics={"times": times, "avg_time": avg_time},
                                    other={},
                                )
                                st.markdown("**Test Results:**")
                                st.markdown(
                                    f"Your test results are [here](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/prompt_templates/{st.session_state.template_id}/variants/{st.session_state.current_variant}/test_suites/{test_template_id}/test_runs/{test_run_id})"
                                )
                                st.markdown(f"```{summary}```")

            except Exception as exc:  # pylint: disable=broad-except
                st.error(f"An error occurred: {exc}")


if __name__ == "__main__":
    main()
