# app.py (version 2 - Universal Connector)

import streamlit as st
import openai

# --- Savant Prompt Template (remains the same) ---
SAVANT_PROMPT_TEMPLATE = """
**Persona:**
You are an expert Product Manager...
(The full prompt from the previous response goes here)
...
**3. Undecided Topics (If Any)**
* List any topics that were discussed but where no clear consensus or final decision was reached. For each, briefly state the point of contention.
"""

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="AI Product Manager for Lighthouse",
    page_icon="💡"
)

# --- Main App UI ---
st.title("💡 Lighthouse AI Product Manager")
st.markdown("Upload an audio recording of a product meeting, and the AI will analyze it to produce detailed requirements and actionable development tasks.")

# --- Universal API Client Initialization ---
# Intelligently determines whether to use Azure OpenAI or standard OpenAI
client = None
try:
    # Check for Azure-specific secrets first
    if st.secrets.get("AZURE_OPENAI_ENDPOINT") and st.secrets.get("AZURE_CHAT_DEPLOYMENT_NAME"):
        st.info("Azure OpenAI environment detected.", icon="🔷")
        client = openai.AzureOpenAI(
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version=st.secrets["OPENAI_API_VERSION"]
        )
        # Get deployment names from secrets
        chat_model_name = st.secrets["AZURE_CHAT_DEPLOYMENT_NAME"]
        whisper_model_name = st.secrets["AZURE_WHISPER_DEPLOYMENT_NAME"]

    # Fallback to standard OpenAI API
    elif st.secrets.get("OPENAI_API_KEY"):
        st.info("Standard OpenAI environment detected.", icon="🟢")
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # Use standard model names
        chat_model_name = "gpt-4o"
        whisper_model_name = "whisper-1"

    else:
        st.error("No valid OpenAI or Azure OpenAI API credentials found in Streamlit secrets.", icon="🚨")
        st.stop()

except Exception as e:
    st.error(f"Error initializing AI client: {e}", icon="🚨")
    st.stop()


# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose an audio file (.mp3, .wav, .m4a)",
    type=['mp3', 'wav', 'm4a']
)

if uploaded_file is not None and client:
    if st.button("Analyze Meeting Audio"):
        try:
            # Stage 1: High-Fidelity Transcription
            with st.spinner('Stage 1/2: Transcribing audio file... This may take a moment.'):
                transcript = client.audio.transcriptions.create(
                    model=whisper_model_name, # Use the determined model/deployment name
                    file=uploaded_file,
                    response_format="text"
                )

            st.info("Transcription complete.", icon="✅")
            with st.expander("View Full Transcript"):
                st.write(transcript)

            # Stage 2: Intelligent Analysis & Requirement Generation
            with st.spinner('Stage 2/2: AI Product Manager is analyzing the transcript...'):
                analysis_response = client.chat.completions.create(
                    model=chat_model_name, # Use the determined model/deployment name
                    messages=[
                        {"role": "system", "content": SAVANT_PROMPT_TEMPLATE},
                        {"role": "user", "content": f"Here is the transcript...\n\n{transcript}"}
                    ],
                    temperature=0.0
                )
                analysis_result = analysis_response.choices[0].message.content

            st.success("Analysis Complete!", icon="🎉")
            st.markdown(analysis_result)

        except Exception as e:
            st.error(f"An error occurred during the analysis: {e}", icon="🚨")
