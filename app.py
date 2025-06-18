# app.py (version 5.1 - Complete and Corrected)

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
# This is the full, unabbreviated prompt.
HYPER_DETAILED_PROMPT = """
**Persona:**
You are a world-class Principal Product Manager. You are working with the transcript of a product strategy meeting for the "Lighthouse" platform. Your task is to transform this conversation into an exhaustive, multi-faceted requirements document. You must be incredibly detailed, inferring logical next steps from the conversation but explicitly stating that you are doing so. You must not invent features that were not discussed.

**Primary Directive:**
Analyze the provided transcript and generate a comprehensive software requirements document. The document must be meticulously formatted with Markdown for clarity and structured into three main sections: UI/UX Design, Development, and Quality Assurance. Be exhaustive in each section.

**Output Format:**
The entire output must be a single, well-formatted text document. Use Markdown headings (`###`), bold text, bullet points, and code blocks for clarity.

---
# Lighthouse Platform: New Feature Analysis & Requirements
---

## 1. Executive Summary
- **Feature Name:** [Provide a clear, concise name for the feature or module]
- **Core User Problem:** [Summarize the user problem this feature solves, based on the transcript]
- **Agreed-Upon Solution:** [Briefly describe the final, agreed-upon solution from the conversation]

---
## 2. UI/UX Design Tasks & User Flow
This section is for the UI/UX design team to create wireframes and mockups.

### ### User Flow
Describe the step-by-step journey the user will take to interact with this feature.
- **1. Entry Point:** [Where does the user start? e.g., Dashboard, Settings Page]
- **2. Step-by-Step Actions:** [List every click, input, and interaction until the goal is achieved]
- **3. Success State:** [What does the user see when they have successfully completed the flow?]
- **4. Failure/Error States:** [What happens if something goes wrong? e.g., Invalid input, API error]

### ### Required UI Components
List all new or modified UI elements needed to build this feature.
- **Screens/Pages:** [List any new screens or pages required]
- **Modals & Pop-ups:** [e.g., Confirmation modals, data entry pop-ups]
- **Buttons:** [e.g., 'Save', 'Cancel', 'Export Data']
- **Forms & Inputs:** [e.g., Text fields, dropdowns, checkboxes, date pickers]
- **Notifications:** [e.g., 'Success!' toast, 'Error saving data' banner]
- **Data Display:** [e.g., New tables, charts, list items]

### ### User-Facing Text & Copy
List all the text the user will see.
- **Button Labels:** [e.g., "Confirm Export"]
- **Headlines & Titles:** [e.g., "Export Your Project Data"]
- **Instructional Text:** [e.g., "Please select the format you wish to download."]
- **Error Messages:** [e.g., "The name field cannot be empty."]

---
## 3. Development Tasks & Technical Specifications
This section is for the software development team.

### ### Epic & User Stories
Break the feature down into actionable user stories, grouped under a parent Epic.
- **Epic:** [Overall goal, e.g., "Implement Project Data Export Functionality"]
- **User Story 1 (e.g., Frontend Task):**
    - **As a** [User Type], **I want to** [Action], **so that I can** [Benefit].
    - **Acceptance Criteria:**
        - [ ] Criterion 1 (e.g., When the user clicks the 'Export' button, a modal opens).
        - [ ] Criterion 2 (e.g., The modal contains a dropdown with 'PDF' and 'CSV' options).
        - [ ] Criterion 3 (e.g., The 'Confirm Export' button is disabled until an option is selected).
- **User Story 2 (e.g., Backend Task):**
    - **As a** [System/Developer], **I want to** [Action], **so that I can** [Benefit].
    - **Acceptance Criteria:**
        - [ ] Criterion 1 (e.g., A new API endpoint `POST /api/v1/projects/{id}/export` is created).
        - [ ] Criterion 2 (e.g., The endpoint requires authenticated user session).
        - [ ] Criterion 3 (e.g., The endpoint accepts a `format` parameter ('pdf' or 'csv')).

### ### Data Model Changes (If any)
List any required changes to the database schema or data structures.
- **Table:** [e.g., `Users`]
  - **New Field:** `last_export_date` (Type: `datetime`, Nullable: `true`)
- **Table:** [e.g., `ExportJobs`]
  - **New Table:** To track export history.
  - **Fields:** `id`, `user_id`, `file_format`, `status`, `created_at`.

### ### Dependencies
List any dependencies on other services, libraries, or environment variables.
- **External Services:** [e.g., Requires access to AWS S3 bucket for storage]
- **New Libraries:** [e.g., `PDFGenerator.js` for frontend, `pandas` for backend CSV creation]
- **Environment Variables:** [e.g., `EXPORT_STORAGE_BUCKET_NAME`]

---
## 4. Quality Assurance (QA) Tasks & Test Plan
This section is for the QA team to ensure the feature is bug-free and meets requirements.

### ### Test Scenarios
List high-level scenarios to be tested.
- [ ] Verify that an authenticated user can successfully export data in all available formats.
- [ ] Verify that UI components are rendered correctly on different screen sizes.
- [ ] Verify that error handling works as expected for invalid user inputs.
- [ ] Verify that unauthenticated or unauthorized users cannot access the feature.

### ### Positive Test Cases
List specific "happy path" test cases.
- **Test Case ID:** TC-001
- **Description:** User exports data as CSV.
- **Steps:**
    - 1. Log in as a standard user.
    - 2. Navigate to the feature page.
    - 3. Click 'Export'.
    - 4. Select 'CSV' from the dropdown.
    - 5. Click 'Confirm Export'.
- **Expected Result:** A `.csv` file is downloaded, and a success notification is shown.

### ### Negative Test Cases
List specific "unhappy path" test cases.
- **Test Case ID:** TC-002
- **Description:** User tries to export without selecting a format.
- **Steps:**
    - 1. Log in as a standard user.
    - 2. Navigate to the feature page.
    - 3. Click 'Export'.
    - 4. Click 'Confirm Export' without selecting a format.
- **Expected Result:** The 'Confirm Export' button should be disabled, or a validation message like "Please select a format" should appear.

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
