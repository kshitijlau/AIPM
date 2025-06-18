# app.py (version 5 - Hyper-Detailed Analysis with Download)

import streamlit as st
import openai
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Requirements Assistant",
    page_icon="💡",
    layout="wide"
)

# --- The New Hyper-Detailed Prompt ---
# (Copy and paste the entire HYPER_DETAILED_PROMPT from above here)
HYPER_DETAILED_PROMPT = """
**Persona:**
You are a world-class Principal Product Manager...
...
### ### Edge Cases
List tests for unlikely but possible scenarios.
- [ ] Test with a project that has no data to export.
- [ ] Test by clicking the 'Confirm Export' button multiple times quickly.
- [ ] Test with user accounts that have special characters in their names.
"""

# --- Functions ---
def get_ai_analysis(transcript_text, api_key, azure_endpoint, deployment_name):
    """
    Initializes the Azure OpenAI client and gets the detailed analysis.
    """
    try:
        client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )

        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": HYPER_DETAILED_PROMPT},
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
st.markdown("Upload a meeting transcript (.txt file) and the AI will generate a comprehensive requirements document for your UI/UX, Dev, and QA teams.")

# --- Secrets Check ---
try:
    azure_secrets = st.secrets["azure_openai"]
    AZURE_API_KEY = azure_secrets["api_key"]
    AZURE_ENDPOINT = azure_secrets["endpoint"]
    AZURE_DEPLOYMENT_NAME = azure_secrets["deployment_name"]
    
    if not all([AZURE_API_KEY, AZURE_ENDPOINT, AZURE_DEPLOYMENT_NAME]):
        st.error("One or more Azure secrets are missing or empty. Please check your app settings.", icon="🚨")
        st.stop()

except KeyError:
    st.error("Azure credentials are not set correctly. Make sure you have an [azure_openai] section in your secrets.", icon="🚨")
    st.stop()


# --- User Interface ---
uploaded_file = st.file_uploader(
    "Upload your meeting transcript",
    type=['txt']
)

if uploaded_file:
    transcript = uploaded_file.getvalue().decode("utf-8")
    
    if st.button("🚀 Generate Full Requirements Document"):
        with st.spinner("Your AI assistant is analyzing the document and generating tasks for all teams... This may take a moment."):
            analysis_result = get_ai_analysis(
                transcript_text=transcript,
                api_key=AZURE_API_KEY,
                azure_endpoint=AZURE_ENDPOINT,
                deployment_name=AZURE_DEPLOYMENT_NAME
            )
        
        if analysis_result:
            st.success("Analysis Complete!", icon="🎉")

            # Display the result in an expander
            with st.expander("View Full Requirements Document", expanded=True):
                st.markdown(analysis_result)
            
            # --- ADD DOWNLOAD BUTTON ---
            # Get current timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"Lighthouse_Requirements_{timestamp}.txt"
            
            st.download_button(
               label="⬇️ Download Requirements as .txt File",
               data=analysis_result.encode('utf-8'), # Encode the string to bytes
               file_name=file_name,
               mime='text/plain' # The MIME type for a plain text file
            )
