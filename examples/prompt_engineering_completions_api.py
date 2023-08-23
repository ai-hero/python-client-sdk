# Streamlit App for OpenAI GPT Completions with F-strings

import streamlit as st
import openai
import re
from dotenv import load_dotenv
import os

# Load OpenAI API Key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    st.title("AI Hero - Prompt Engineering with OpenAI Completions API")

    # Using Sidebar for Prompt Template and Settings
    st.sidebar.write("**Prompt Template:**")
    template = st.sidebar.text_area(
        "Enter your f-string prompt template:",
        """Translate the following text into Japanese:\n{text}\n\nTranslation:""",
        key="1",
        height=450,
    )

    # Spacing
    st.sidebar.text("")
    st.sidebar.text("")

    # Advanced settings within a collapsible section in the sidebar

    with st.sidebar.expander("Settings", expanded=False):
        st.sidebar.write("**Advanced model and query settings:**")
        engine = st.sidebar.text_input("Model name:", "text-davinci-003", key="2")
        temperature = st.sidebar.text_input("Temperature:", "0.7", key="3")

    # Extract f-string variables and provide input boxes on the main area
    variables = extract_fstring_variables(template)
    user_inputs = {}
    for var in variables:
        user_inputs[var] = st.text_input(
            f"Enter value for {var}",
            key=f"input_{var}",
        )

    # Spacing
    st.text("")

    # Button to generate completion
    if st.button("Generate"):
        # Indicate process is running
        with st.spinner("Running..."):
            # Fill the f-string using user inputs
            filled_template = template.format(**user_inputs)

            # Get completion from OpenAI API
            response = openai.Completion.create(
                engine=engine, prompt=filled_template, temperature=float(temperature)
            )

            # Displaying the completion as text
            st.markdown("**Completion:**")
            st.text(response.choices[0].text)


if __name__ == "__main__":
    main()
