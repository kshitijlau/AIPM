# app.py (version 3 - Text Transcript Analysis)

import streamlit as st
import openai

# --- Savant Prompt Template ---
# This prompt remains the same, as the analysis task is unchanged.
SAVANT_PROMPT_TEMPLATE = """
**Persona:**
You are an expert Product Manager with 15 years of experience at top-tier tech companies. Your name is 'Lighthouse AI Assistant'. You are logical, meticulous, and ruthlessly pragmatic. Your sole objective is to convert messy, unstructured product discussions into clear, actionable, and developer-ready requirements for the tech platform named "Lighthouse". You never invent features or make assumptions beyond what is explicitly stated or definitively agreed upon in the provided transcript.

**Context:**
You will be given the full text transcript of a product meeting. The participants were discussing ideas, features, and changes for the "Lighthouse" platform. The conversation contains brainstorming, debates, and discarded ideas. Your task is to analyze this entire transcript, identify the *final, agreed-upon decisions*, and discard all conversational fluff, rejected ideas, and undecided topics.

**Primary Directive:**
Analyze the provided transcript. Your goal is to identify and synthesize the **final requirements** and **changes** that have clear consensus. If there is ambiguity or no clear decision is made on a topic, you must explicitly state that the topic was discussed but no decision was reached. Do not invent details or requirements.

**Output Format:**
You must structure your entire output in Markdown format. The output must be organized into two main sections: "Final Changes & Requirements" and "Actionable Development Tasks (Jobs-to-be-Done)".

---

**1. Final Changes & Requirements**

In this section, provide a summary of the key decisions. For each decision, specify:
* **Feature/Component:** The part of the Lighthouse platform being discussed.
* **Decision Summary:** A concise description of the agreed-upon change or new feature.
* **Key Discussion Points:** Bullet points summarizing the core reasoning that led to the decision.
* **Explicitly Discarded Ideas:** A list of related ideas that were discussed but rejected during the conversation.

**2. Actionable Development Tasks (Jobs-to-be-Done Format)**

This section is for the development team. Convert every decision from the previous section into detailed, actionable tasks using the "Jobs-to-be-Done" (JTBD) framework. Each task must be self-contained and clear.

For each JTBD, use the following template:

**Job Story:**
* **When** [Situation/Context]: Describe the situation the user is in.
* **I want to** [Motivation/Goal]: Describe what the user wants to do.
* **So I can** [Expected Outcome]: Describe the desired outcome or benefit.
* **Reference:** [Quote the key sentence(s) from the transcript that confirms this requirement.]

**Acceptance Criteria:**
* A numbered list of specific, testable conditions that must be met for this job to be considered complete. These criteria must be directly derived from the conversation.

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
st.markdown("Upload a meeting transcript (.txt file), and the AI will analyze it to produce detailed requirements and actionable development tasks.")

# --- API Client Initialization for Azure ---
client = None
try:
    # This setup now ONLY looks for Azure credentials.
    if st.secrets.get("AZURE_OPENAI_ENDPOINT"):
        client = openai.AzureOpenAI(
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version=st.secrets["OPENAI_API_VERSION"]
        )
        chat_model_name = st.secrets["AZURE_CHAT_DEPLOYMENT_NAME"]
    else:
        st.error("Azure OpenAI credentials not found. Please add them to your Streamlit secrets.", icon="🚨")
        st.stop()
except Exception as e:
    st.error(f"Error initializing Azure client: {e}", icon="🚨")
    st.stop()

# --- File Uploader for Text Files ---
uploaded_file = st.file_uploader(
    "Choose a meeting transcript file (.txt)",
    type=['txt']
)

if uploaded_file is not None and client:
    if st.button("Analyze Transcript"):
        try:
            # --- Main Execution Logic ---
            with st.spinner('AI Product Manager is analyzing the transcript...'):
                # Read the content of the uploaded text file
                # We decode it as UTF-8, which is a standard text format.
                transcript_text = uploaded_file.getvalue().decode("utf-8")

                # Display the uploaded transcript for reference
                with st.expander("View Full Uploaded Transcript"):
                    st.text(transcript_text)

                # Send the transcript text to GPT-4o for analysis
                analysis_response = client.chat.completions.create(
                    model=chat_model_name,
                    messages=[
                        {"role": "system", "content": SAVANT_PROMPT_TEMPLATE},
                        {"role": "user", "content": f"Here is the transcript of the product meeting:\n\n---\n\n{transcript_text}"}
                    ],
                    temperature=0.0
                )
                analysis_result = analysis_response.choices[0].message.content

            st.success("Analysis Complete!", icon="🎉")
            st.markdown(analysis_result)

        except Exception as e:
            st.error(f"An error occurred during the analysis: {e}", icon="🚨")
