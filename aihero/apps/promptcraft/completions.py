import os
import re
import time
from datetime import date
from uuid import uuid4

import openai
import httpx
import pandas as pd
import streamlit as st
import validators
from dotenv import load_dotenv
from text_generation import Client

from aihero import promptstash
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
    """Extracts f-string variables from a template string."""
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
    st.sidebar.title("PromptCraft")
    st.sidebar.markdown("This app is powered by [AI Hero](https://app.aihero.studio).")
    # Using Sidebar for Prompt Template and Settings
    st.sidebar.write("**Step 1: Prompt Template:**")
    st.session_state.model_set = False
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
            try:
                st.session_state.current_template = ps.variant(
                    template_id=st.session_state.template_id
                )
            except Exception:  # pylint: disable=broad-except
                st.session_state.current_template = """Translate the following text into Japanese.\nText: {text}\nTranslation: """

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

        # Advanced RAG collapsible section in the sidebar
        with st.sidebar.expander(
            "Retrieval Augmented Generation (optional)", expanded=False
        ):
            st.write("**Optional: Settings for RAG:**")
            st.write(
                "Point to an API server that takes a JSON object of your inputs, and returns context as JSON."
            )
            st.session_state.use_rag = st.checkbox(
                "Use RAG from server", False, key="30"
            )
            if st.session_state.use_rag:
                st.session_state.rag_inputs = []
                # Host
                st.session_state.rag_server = st.text_input(
                    "RAG Host:", "http://127.0.0.1:5000", key="31"
                )
                try:
                    # assert is url
                    validators.url(st.session_state.rag_server)
                except validators.ValidationFailure:
                    st.error(f"'{st.session_state.rag_server}' is not a valid URL.")
                    st.stop()

                # Host
                st.session_state.rag_cs_inputs = st.text_input(
                    "Input variables to the RAG service (comma separated list of vars):",
                    "text",
                    key="32",
                )
                try:
                    # Parsing the input string into a list of values
                    values = []
                    for value in st.session_state.rag_cs_inputs.split(","):
                        if value.strip():
                            values.append(value)

                    # Validating the values (Here, we are just checking if they are non-empty and are alphanumeric)
                    for value in values:
                        assert value and value.isalnum()

                    st.session_state.rag_inputs = values
                except AssertionError:
                    st.error(
                        f"'{st.session_state.rag_cs_inputs}' is not a valid comma separated list of variables."
                    )
                    st.stop()

        # Advanced settings within a collapsible section in the sidebar
        with st.sidebar.expander("Settings", expanded=False):
            st.write("**Optional:**")
            st.write("**Advanced model and query settings:**")
            st.session_state.OPENAI_MODELS = ["text-davinci-003", "text-davinci-002"]
            selections = []
            selections.extend(st.session_state.OPENAI_MODELS)
            selections.append("private-tgi")
            st.session_state.engine = st.selectbox(
                "Model name:",
                selections,
                index=0,
                key="2",
            )

            if st.session_state.engine in st.session_state.OPENAI_MODELS:
                if "OPENAI_API_KEY" not in os.environ:
                    st.error(
                        (
                            "Error: Missing key OPENAI_API_KEY in .env file: "
                            "Get the necessary keys from [OpenAI](https://openai.com)"
                        )
                    )
                else:
                    st.session_state.model_set = True
            elif st.session_state.engine == "private-tgi":
                st.session_state.host = st.text_input(
                    "Host:", "http://localhost:8081", key="25"
                )
                st.session_state.model_set = True

            # Temperature
            st.session_state.temperature = st.text_input(
                "Temperature (from 0 to 1):", "0.7", key="3"
            )
            try:
                assert (
                    float(st.session_state.temperature) >= 0
                    and float(st.session_state.temperature) <= 1
                )
            except (ValueError, AssertionError):
                st.error(
                    f"'{st.session_state.temperature}' is not a valid temperature. It should be a number between 0 and 1."
                )
                st.stop()

            # Max Tokens
            st.session_state.max_tokens = st.text_input(
                "Max Tokens (depends on model):", "256", key="6"
            )
            try:
                assert int(st.session_state.max_tokens) > 0 and int(
                    st.session_state.max_tokens
                ) <= (32 * 1024)
            except (ValueError, AssertionError):
                st.error(
                    f"'{st.session_state.max_tokens}' is not a valid number. It should be a number greater than 0."
                )
                st.stop()

            # Top-p
            st.session_state.top_p = st.text_input(
                "Top-p (from 0 to 1):", "1", key="15"
            )
            try:
                assert (
                    float(st.session_state.top_p) >= 0
                    and float(st.session_state.top_p) <= 1
                )
            except (ValueError, AssertionError):
                st.error(
                    f"'{st.session_state.top_p}' is not a valid top_p. It should be a number between 0 and 1."
                )
                st.stop()

            st.session_state.model = {
                "name": st.session_state.engine,
                "engine": st.session_state.engine,
                "temperature": float(st.session_state.temperature),
                "max_tokens": int(st.session_state.max_tokens),
                "top_p": float(st.session_state.top_p),
                "version": date.today().strftime("%Y-%m-%d"),
            }

            if st.session_state.engine in st.session_state.OPENAI_MODELS:
                # Presence Penalty
                st.session_state.presence_penalty = st.text_input(
                    "Presence Penalty (from -2 to 2):", "0", key="16"
                )
                try:
                    assert (
                        float(st.session_state.presence_penalty) >= -2
                        and float(st.session_state.presence_penalty) <= 2
                    )
                except (ValueError, AssertionError):
                    st.error(
                        f"'{st.session_state.presence_penalty}' is not a valid presence penalty. It should be a number between -2 and 2."
                    )
                    st.stop()

                # Frequency Penalty
                st.session_state.frequency_penalty = st.text_input(
                    "Frequency Penalty (from -2 to 2):", "0", key="17"
                )
                try:
                    assert (
                        float(st.session_state.frequency_penalty) >= -2
                        and float(st.session_state.frequency_penalty) <= 2
                    )
                except (ValueError, AssertionError):
                    st.error(
                        f"'{st.session_state.frequency_penalty}' is not a valid frequency penalty. It should be a number between -2 and 2."
                    )
                    st.stop()

                st.session_state.model["presence_penalty"] = (
                    float(st.session_state.presence_penalty),
                )
                st.session_state.model["frequency_penalty"] = (
                    float(st.session_state.frequency_penalty),
                )

    st.title("PromptCraft using OpenAI Completions API")
    st.markdown(
        "PromptCraft, by AI Hero, is the fastest way for product managers and prompt engineers to iterate on a prompt and share it with their engineering team. Working along-side PromptStash, PromptCraft allows you to collaboratively develop, refine, and test prompts. Once ready, your engineering team can retrieve your best prompt template using PromptStash and deploy it to production."
    )
    if not st.session_state.model_set:
        st.warning(
            "Please select a model in the sidebar on the left. You can also change the default settings."
        )
        st.stop()
    elif not st.session_state.template_id.strip():
        st.warning("Please enter a template ID in the sidebar on the left.")
        st.stop()
    elif not st.session_state.template.strip():
        st.warning("Please enter your prompt template in the sidebar on the left.")
        st.stop()

    try_it_out, evaluation = st.tabs(["Try it Out", "Evaluation"])

    with try_it_out:
        # Extract f-string variables and provide input boxes on the main area
        variables = extract_fstring_variables(st.session_state.template)
        st.session_state.user_inputs = {}
        for var in variables:
            if st.session_state.use_rag is True:
                if var in st.session_state.rag_inputs:
                    st.session_state.user_inputs[var] = st.text_input(
                        f"Enter value for {var}",
                        key=f"input_{var}",
                    )
                else:
                    st.text(f"Expecting '{var}' in retrieved context.")
            else:
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
                # Check if inputs are present
                for var in variables:
                    if st.session_state.use_rag:
                        if (
                            var in st.session_state.rag_inputs
                            and not st.session_state.user_inputs[var].strip()
                        ):
                            st.error(f"Missing value for variable '{var}'")
                            st.stop()
                    else:
                        if not st.session_state.user_inputs[var].strip():
                            st.error(f"Missing value for variable '{var}'")
                            st.stop()

                # Retrieve the context
                if st.session_state.use_rag is True:
                    # Using HTTPX to send a POST request
                    with httpx.Client() as client:
                        r = client.post(
                            st.session_state.rag_server,
                            json=st.session_state.user_inputs,
                        )

                    # Checking if the request was successful
                    if r.status_code == 200:
                        st.session_state.user_inputs.update(r.json())
                    else:
                        st.error(f"Failed with status code {r.status_code}: {r.text}")
                        st.stop()

                # Check if retrieved context are present
                for var in variables:
                    if st.session_state.use_rag:
                        if (
                            var in st.session_state.rag_inputs
                            and not st.session_state.user_inputs[var].strip()
                        ):
                            st.error(f"Missing value for variable '{var}'")
                            st.stop()
                        elif (
                            var not in st.session_state.user_inputs
                            or not st.session_state.user_inputs[var].strip()
                        ):
                            st.error(f"Missing value for variable '{var}'")
                            st.stop()
                    else:
                        if not st.session_state.user_inputs[var].strip():
                            st.error(f"Missing value for variable '{var}'")
                            st.stop()

                trace_id = str(uuid4())
                step_id = str(uuid4())
                filled_template = st.session_state.template.format(
                    **st.session_state.user_inputs
                )
                prompt = filled_template

                inputs = st.session_state.user_inputs
                rendered_inputs = "\n\n".join([f"{k}: {v}" for k, v in inputs.items()])

                # Capture the start time (tic) right before making the API call
                tic = time.perf_counter()

                if st.session_state.engine == "private-tgi":
                    client = Client("http://127.0.0.1:8081")
                    top_p_tgi = float(st.session_state.top_p)
                    if top_p_tgi >= 1:
                        top_p_tgi = 0.99
                    response = client.generate(
                        filled_template,
                        temperature=float(st.session_state.temperature),
                        max_new_tokens=int(st.session_state.max_tokens),
                        top_p=top_p_tgi,
                    )
                    # if not response.token.special:
                    #     text += response.token.text
                    output = response.generated_text.encode("utf-8").decode("utf-8")
                    usage = {
                        "generated_tokens": response.details.generated_tokens,
                        "seed": response.details.seed,
                    }
                elif st.session_state.engine in st.session_state.OPENAI_MODELS:
                    # Get completion from OpenAI API
                    response = openai.Completion.create(
                        engine=st.session_state.engine,
                        prompt=filled_template,
                        temperature=float(st.session_state.temperature),
                        max_tokens=int(st.session_state.max_tokens),
                        top_p=float(st.session_state.top_p),
                        presence_penalty=float(st.session_state.presence_penalty),
                        frequency_penalty=float(st.session_state.frequency_penalty),
                    )
                    output = response.choices[0].text
                    usage = response.usage

                # Capture the end time (toc) after getting the response
                toc = time.perf_counter()
                print(f"Time taken: {toc - tic}")

                # Displaying the completion as text
                st.subheader("Prompt: ")
                st.markdown(filled_template)
                st.subheader("Completion: ")
                st.markdown(output)

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
                    other={"usage": usage},
                )

                st.markdown(
                    f"You can see your trace saved with the trace_id `{trace_id}` [here](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/traces)"
                )

    # Test Suite
    with evaluation:
        st.markdown(
            "First, upload the tet suite CSV. The CSV should have only one column. Each row should \
            be an expectation (question or statement) you expect of the prompt completion. \
            You can find an example [here](https://github.com/ai-hero/python-client-sdk/tree/main/examples/test_suite.csv)"
        )
        test_suite_file = st.file_uploader(
            "Upload test suite of expectations", type=["csv"]
        )
        if not test_suite_file:
            st.error("Test Suite file not found.")
            st.stop()

        test_suite_df = pd.read_csv(test_suite_file, header=None)
        if len(test_suite_df.columns) != 1:
            st.error("Should only have one column.")

        expectations = [
            [v for v in test_suite_df[col].astype(str).tolist() if v]
            for col in test_suite_df.columns
        ]

        test_template_id = f"{st.session_state.template_id}-test"

        test_suite = ps.build_test_suite(test_suite_id=test_template_id)

        st.markdown(
            "Next, upload the tet cases CSV. The CSV should have one column for your inputs. Each row should be a test case. \
            If you're using RAG, then you should only include your inputs and not the RAG returned values. \
            You can find an example [here](https://github.com/ai-hero/python-client-sdk/tree/main/examples/j2e.csv)"
        )

        # Upload CSV file
        test_cases_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if not test_cases_file:
            st.error("Test Cases file not found.")
            st.stop()

        test_cases_df = pd.read_csv(test_cases_file)

        try:
            # Check if all required columns exist in the uploaded CSV
            missing_columns = []
            for var in variables:
                if st.session_state.use_rag:
                    if (
                        var in st.session_state.rag_inputs
                        and var not in test_cases_df.columns
                    ):
                        missing_columns.append(var)
                else:
                    if var not in test_cases_df.columns:
                        missing_columns.append(var)

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
                    for index, row in test_cases_df.iterrows():
                        # Update session state user_inputs for the current row
                        st.session_state.user_inputs = row.to_dict()

                        # Check if inputs are present
                        for var in variables:
                            if st.session_state.use_rag:
                                if (
                                    var in st.session_state.rag_inputs
                                    and not st.session_state.user_inputs[var].strip()
                                ):
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()
                            else:
                                if not st.session_state.user_inputs[var].strip():
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()

                        # Retrieve the context
                        if st.session_state.use_rag is True:
                            # Using HTTPX to send a POST request
                            with httpx.Client() as client:
                                r = client.post(
                                    st.session_state.rag_server,
                                    json=st.session_state.user_inputs,
                                )

                            # Checking if the request was successful
                            if r.status_code == 200:
                                st.session_state.user_inputs.update(r.json())
                            else:
                                st.error(
                                    f"Failed with status code {r.status_code}: {r.text}"
                                )
                                st.stop()

                        # Check if retrieved context are present
                        for var in variables:
                            if st.session_state.use_rag:
                                if (
                                    var in st.session_state.rag_inputs
                                    and not st.session_state.user_inputs[var].strip()
                                ):
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()
                                elif not st.session_state.user_inputs[var].strip():
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()
                            else:
                                if not st.session_state.user_inputs[var].strip():
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()

                        filled_template = st.session_state.template.format(
                            **st.session_state.user_inputs
                        )
                        prompt = filled_template
                        inputs = st.session_state.user_inputs
                        rendered_inputs = "\n\n".join(
                            [f"{k}: {v}" for k, v in inputs.items()]
                        )

                        # Capture the start time (tic) right before making the API call
                        tic = time.perf_counter()

                        if st.session_state.engine == "private-tgi":
                            client = Client("http://127.0.0.1:8081")
                            top_p_tgi = float(st.session_state.top_p)
                            if top_p_tgi >= 1:
                                top_p_tgi = 0.99
                            response = client.generate(
                                filled_template,
                                temperature=float(st.session_state.temperature),
                                max_new_tokens=int(st.session_state.max_tokens),
                                top_p=top_p_tgi,
                            )
                            # if not response.token.special:
                            #     text += response.token.text
                            output = response.generated_text.encode("utf-8").decode(
                                "utf-8"
                            )
                            usage = {
                                "generated_tokens": response.details.generated_tokens,
                                "seed": response.details.seed,
                            }
                        elif st.session_state.engine in st.session_state.OPENAI_MODELS:
                            # Get completion from OpenAI API
                            response = openai.Completion.create(
                                engine=st.session_state.engine,
                                prompt=filled_template,
                                temperature=float(st.session_state.temperature),
                                max_tokens=int(st.session_state.max_tokens),
                                top_p=float(st.session_state.top_p),
                                presence_penalty=float(
                                    st.session_state.presence_penalty
                                ),
                                frequency_penalty=float(
                                    st.session_state.frequency_penalty
                                ),
                            )
                            output = response.choices[0].text
                            usage = response.usage

                        # Capture the end time (toc) after getting the response
                        toc = time.perf_counter()

                        # Displaying the completion as text for each row
                        st.header(f"Row {index + 1}:")
                        st.subheader("Prompt: ")
                        st.markdown(filled_template)
                        st.subheader("Completion: ")
                        st.markdown(output)

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
                            expectations=expectations,
                            model=st.session_state.model,
                            metrics={"times": times, "avg_time": avg_time},
                            other={},
                        )
                        st.markdown("**Test Results:**")
                        st.markdown(
                            f"Your test results are [here](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/prompt_templates/{st.session_state.template_id}/variants/{st.session_state.current_variant}/test_suites/{test_template_id}/test_runs/{test_run_id})"
                        )
                        st.markdown(f"~~~{summary}~~~")

        except Exception as exc:  # pylint: disable=broad-except
            st.error(f"An error occurred: {exc}")


if __name__ == "__main__":
    main()
