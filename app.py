# app.py

import streamlit as st
import openai

# --- Page Configuration ---
# This should be the first Streamlit command in your script.
st.set_page_config(
    page_title="AI Requirements Assistant",
    page_icon="💡",
    layout="wide"
)

# --- Functions ---
# It's good practice to put your core logic into functions.
def get_ai_analysis(transcript_text, api_key, azure_endpoint, deployment_name):
    """
    Initializes the Azure OpenAI client and gets the analysis.
    
    Args:
        transcript_text (str): The meeting transcript.
        api_key (str): Your Azure OpenAI API key.
        azure_endpoint (str): Your Azure OpenAI endpoint URL.
        deployment_name (str): Your GPT-4o deployment name.
        
    Returns:
        str: The analysis result from the AI model.
    """
    try:
        # Initialize the client with credentials from st.secrets
        client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"  # A common, stable API version
        )
        
        # The prompt for the AI Product Manager
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
        # Gracefully handle potential errors, like authentication issues
        st.error(f"An error occurred while contacting the AI service: {e}", icon="🚨")
        return None

# --- Main Application ---

st.title("💡 AI Requirements Assistant")
st.markdown("Upload a meeting transcript (.txt file) and the AI will analyze it to produce detailed requirements.")

# --- Step 1: Securely check for secrets ---
# We use a try-except block to ensure the app doesn't crash if secrets are missing.
try:
    AZURE_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
    AZURE_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
    AZURE_DEPLOYMENT_NAME = st.secrets["AZURE_CHAT_DEPLOYMENT_NAME"]
    
    # A simple check to see if keys are present but empty
    if not all([AZURE_API_KEY, AZURE_ENDPOINT, AZURE_DEPLOYMENT_NAME]):
        st.error("One or more Azure secrets are missing or empty. Please check your app settings.", icon="🚨")
        st.stop()

except KeyError:
    st.error("Azure credentials are not set. Please add them in the app settings on Streamlit Cloud.", icon="🚨")
    st.info("Required secrets: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_CHAT_DEPLOYMENT_NAME")
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
