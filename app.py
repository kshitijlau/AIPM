# app.py (version 4 - Using TOML Sections for Secrets)

import streamlit as st
import openai

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Requirements Assistant",
    page_icon="💡",
    layout="wide"
)

# --- Functions ---
def get_ai_analysis(transcript_text, api_key, azure_endpoint, deployment_name):
    """
    Initializes the Azure OpenAI client and gets the analysis.
    """
    try:
        client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
        
        savant_prompt = """
        **Persona:**
        You are an expert Product Manager...
        (Insert the full, detailed prompt here as in the previous examples)
        """
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": savant_prompt},
                {"role": "user", "content": transcript_text}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"An error occurred while contacting the AI service: {e}", icon="🚨")
        return None

# --- Main Application ---

st.title("💡 AI Requirements Assistant")
st.markdown("Upload a meeting transcript (.txt file) and the AI will analyze it to produce detailed requirements.")

# --- Step 1: Securely check for secrets using the new structure ---
try:
    # Access the secrets through the 'azure_openai' section
    azure_secrets = st.secrets["azure_openai"]
    AZURE_API_KEY = azure_secrets["api_key"]
    AZURE_ENDPOINT = azure_secrets["endpoint"]
    AZURE_DEPLOYMENT_NAME = azure_secrets["deployment_name"]
    
    # A simple check to see if keys are present but empty
    if not all([AZURE_API_KEY, AZURE_ENDPOINT, AZURE_DEPLOYMENT_NAME]):
        st.error("One or more Azure secrets are missing or empty within the [azure_openai] section. Please check your app settings.", icon="🚨")
        st.stop()

except KeyError:
    st.error("Azure credentials are not set correctly. Make sure you have an [azure_openai] section in your secrets.", icon="🚨")
    st.info("Required structure:\n[azure_openai]\napi_key = \"...\"\nendpoint = \"...\"\ndeployment_name = \"...\"")
    st.stop()


# --- Step 2: The User Interface ---
uploaded_file = st.file_uploader(
    "Upload your meeting transcript",
    type=['txt']
)

if uploaded_file:
    transcript = uploaded_file.getvalue().decode("utf-8")
    
    st.expander("View Uploaded Transcript").text(transcript)

    if st.button("✨ Analyze Transcript"):
        with st.spinner("Your AI assistant is analyzing the document..."):
            analysis_result = get_ai_analysis(
                transcript_text=transcript,
                api_key=AZURE_API_KEY,
                azure_endpoint=AZURE_ENDPOINT,
                deployment_name=AZURE_DEPLOYMENT_NAME
            )
        
        if analysis_result:
            st.success("Analysis Complete!", icon="🎉")
            st.markdown(analysis_result)
