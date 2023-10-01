import os
import re
import time
from copy import deepcopy
from datetime import date
from uuid import uuid4

import openai
import httpx
import pandas as pd
import streamlit as st
import validators
from dotenv import load_dotenv

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
    """Extracts f-string variables from a template string."""
    return list(set(re.findall(r"\{(\w+)\}", template)))


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

    st.session_state.template_id = st.sidebar.text_input(
        "Template ID:", "japanese-tutor", key="4"
    )
    st.session_state.template = ""

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
                st.session_state.current_template = [
                    {
                        "role": "system",
                        "content": "You are a Japanese language tutor. The user is a student who wants to learn Japanese. Before we begin, you will welcome the user and explain your role. The user will type something in English.  To this, you will first translate what the user said in Japanese (include a pronunciation guide in brackets).  Next, you'll respond to the user chat in Japanese (include a production guide in brackets). Finally, Include the translation of what you said in English and an explanation of the grammar or vocabulary in the response.",
                    }
                ]

        st.sidebar.divider()
        st.sidebar.write("**Step 2: Enter the System Prompt:**")

        st.session_state.system_message = st.sidebar.text_area(
            "Enter your initial instructions describing who the Agent is:",
            st.session_state.current_template[0]["content"],
            key="1",
            height=400,
        ).strip()

        st.session_state.template = [
            {
                "role": "system",
                "content": st.session_state.system_message,
            }
        ]

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
            st.session_state.model = st.selectbox(
                "Model name:",
                [
                    "gpt-4",
                    "gpt-4-0613",
                    "gpt-4-32k",
                    "gpt-4-32k-0613",
                    "gpt-3.5-turbo",
                    "gpt-3.5-turbo-0613",
                    "gpt-3.5-turbo-16k",
                    "gpt-3.5-turbo-16k-0613",
                ],
                index=4,
                key="2",
            )
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

            st.session_state.model = {
                "name": st.session_state.model,
                "model": st.session_state.model,
                "temperature": float(st.session_state.temperature),
                "max_tokens": int(st.session_state.max_tokens),
                "top_p": float(st.session_state.top_p),
                "presence_penalty": float(st.session_state.presence_penalty),
                "frequency_penalty": float(st.session_state.frequency_penalty),
                "version": date.today().strftime("%Y-%m-%d"),
            }

    st.title("PromptCraft using OpenAI Chat Completions API")
    st.markdown(
        "PromptCraft, by AI Hero, is the fastest way for product managers and prompt engineers to iterate on a prompt and share it with their engineering team. Working along-side PromptStash, PromptCraft allows you to collaboratively develop, refine, and test prompts. Once ready, your engineering team can retrieve your best prompt template using PromptStash and deploy it to production."
    )
    if not st.session_state.template_id.strip():
        st.warning("Please enter a template ID in the sidebar on the left.")
        st.stop()
    elif not st.session_state.template:
        st.warning("Please enter your prompt template in the sidebar on the left.")
        st.stop()

    # Extract f-string variables and provide input boxes on the main area
    variables = extract_fstring_variables(st.session_state.template[0]["content"])
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

    st.session_state.mode = st.selectbox(
        "Mode:",
        [
            "Try It Out",
            "Evaluation",
        ],
        index=0,
        key="50",
    )

    if st.session_state.mode == "Try It Out":
        # Initialize chat history
        if "messages" not in st.session_state:
            print("Initializing messages")
            st.session_state.messages = []
            st.session_state.trace_id = str(uuid4())

        if st.button("Restart"):
            st.session_state.messages.clear()
            st.session_state.trace_id = str(uuid4())

        if not st.session_state.messages:
            st.session_state.template[0]["content"] = st.session_state.template[0][
                "content"
            ].format(**st.session_state.user_inputs)
            st.session_state.messages.extend(deepcopy(st.session_state.template))

        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if content := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": content})
            with st.chat_message("user"):
                st.write(content)

        # Generate a new response if last message is not from assistant
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Capture the start time (tic) right before making the API call
                    tic = time.perf_counter()
                    print("Requesting completion...")
                    # Get completion from OpenAI API
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=st.session_state.messages,
                        temperature=float(st.session_state.temperature),
                        max_tokens=int(st.session_state.max_tokens),
                        top_p=int(st.session_state.top_p),
                        presence_penalty=float(st.session_state.presence_penalty),
                        frequency_penalty=float(st.session_state.frequency_penalty),
                    )

                    # Capture the end time (toc) after getting the response
                    toc = time.perf_counter()

                    step_id = str(uuid4())
                    inputs = st.session_state.user_inputs
                    rendered_inputs = "\n\n".join(
                        [f"{k}: {v}" for k, v in inputs.items()]
                    )

                    ps.stash_completion(
                        trace_id=st.session_state.trace_id,
                        step_id=step_id,
                        template_id=st.session_state.template_id,
                        variant=st.session_state.current_variant,
                        prompt=st.session_state.messages,
                        output=completion.choices[0].message,
                        inputs=inputs,
                        rendered_inputs=rendered_inputs,
                        model=st.session_state.model,
                        metrics={"time": (toc - tic), "usage": completion.usage},
                        other={},
                    )
                st.write(completion.choices[0].message["content"])
            st.session_state.messages.append(completion.choices[0].message)
            st.markdown(
                f"You can see your trace saved with the trace_id `{st.session_state.trace_id}` [here](https://app.aihero.studio/v1/tools/promptstash/projects/{AI_HERO_PROJECT_ID}/traces)"
            )

    # Test Suite
    elif st.session_state.mode == "Evaluation":
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
            You can find an example [here](https://github.com/ai-hero/python-client-sdk/tree/main/examples/j2e_chat.csv)"
        )

        # Upload CSV file
        test_cases_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if not test_cases_file:
            st.error("Test Cases file not found.")
            st.stop()

        test_cases_df = pd.read_csv(test_cases_file)

        try:
            if "chat" not in test_cases_df.columns:
                st.error(
                    f"Uploaded CSV is missing the following columns: {', '.join(['chat'])}"
                )
            else:
                st.success("CSV file successfully uploaded and columns match!")

                # Your provided code starts here
                with st.spinner("Running..."):
                    completions = []
                    times = []
                    for index, row in test_cases_df.iterrows():
                        # Update session state user_inputs for the current row
                        row_inputs = row.to_dict()
                        row_inputs.update(st.session_state.user_inputs)

                        # Check if inputs are present
                        for var in variables:
                            if st.session_state.use_rag:
                                if (
                                    var in st.session_state.rag_inputs
                                    and not row_inputs[var].strip()
                                ):
                                    st.error(f"Missing value for variable '{var}'")
                                    st.stop()
                            else:
                                if var not in row_inputs or not row_inputs[var].strip():
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

                        st.session_state.template[0][
                            "content"
                        ] = st.session_state.template[0]["content"].format(
                            **st.session_state.user_inputs
                        )

                        inputs = st.session_state.user_inputs
                        rendered_inputs = "\n\n".join(
                            [f"{k}: {v}" for k, v in inputs.items()]
                        )

                        # Capture the start time (tic) right before making the API call
                        tic = time.perf_counter()

                        test_messages = deepcopy(st.session_state.template)
                        test_messages.append({"role": "user", "content": row["chat"]})
                        # Get completion from OpenAI API
                        completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=test_messages,
                            temperature=float(st.session_state.temperature),
                            max_tokens=int(st.session_state.max_tokens),
                            top_p=int(st.session_state.top_p),
                            presence_penalty=float(st.session_state.presence_penalty),
                            frequency_penalty=float(st.session_state.frequency_penalty),
                        )
                        # Capture the end time (toc) after getting the response
                        toc = time.perf_counter()

                        # Displaying the completion as text for each row
                        st.header(f"Row {index + 1}:")
                        st.subheader("Inputs: ")
                        st.markdown(
                            "\n\n".join(
                                [
                                    f"**{msg['role']}:** {msg['content']}"
                                    for msg in test_messages
                                ]
                            )
                        )
                        st.subheader("Completion: ")
                        st.markdown(completion.choices[0].message["content"])

                        this_time = toc - tic

                        completions.append(
                            {
                                "inputs": inputs,
                                "rendered_inputs": rendered_inputs,
                                "prompt": st.session_state.messages,
                                "output": completion.choices[0].message,
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
