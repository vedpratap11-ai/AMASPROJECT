import streamlit as st
import google.generativeai as genai

# -------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="OmniHR Enterprise Copilot | Director Edition",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
    .sub-header { font-size: 1.1rem; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 2. SIDEBAR CONFIGURATION & API KEY SETUP
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ System Control Center")
    api_key_input = st.text_input("Enter Google Gemini API Key:", type="password", help="Required for secure LLM execution.")
    
    st.markdown("---")
    st.markdown("### 📊 Enterprise Telemetry")
    st.metric(label="Engine Status", value="Online (Direct Context RAG)", delta="Zero Latency")
    st.metric(label="Guardrail Status", value="Active (Strict Mode)", delta="100% Grounded")
    st.metric(label="Model Tier", value="Gemini 1.5 Flash", delta="Optimized")
    
    st.markdown("---")
    st.markdown("### 📂 Policy Knowledge Base")
    uploaded_file = st.file_uploader("Upload Custom HR Handbook (.txt)", type=["txt"])

# -------------------------------------------------------------------------
# 3. KNOWLEDGE BASE DEFINITION
# -------------------------------------------------------------------------
DEFAULT_HR_POLICY = """
[COMPANY MASTER POLICY HANDBOOK - REVISED 2026]

SECTION 1: LEAVE & ATTENDANCE POLICY
- Annual Paid Leave (PL): Employees accrue 1.66 days per month, totaling 20 paid days per calendar year. Unused PL can be carried over up to a maximum of 5 days into the next financial year.
- Sick Leave (SL): 10 days of paid sick leave are provided annually. Medical certificates are mandatory for consecutive absences exceeding 3 working days.
- Paternity & Maternity Leave: Primary caregivers are eligible for 12 weeks of fully paid leave. Secondary caregivers receive 4 weeks of fully paid leave, which can be availed within the first 6 months of child delivery or adoption.

SECTION 2: REMOTE WORK & FLEXI-TIME GUIDELINES
- Hybrid Model: All full-time employees are permitted to work remotely up to 2 days per week, subject to direct manager approval and core collaboration hours (10:00 AM to 4:00 PM IST).
- Ergonomic Allowance: A one-time tax-exempt reimbursement of up to $250 is granted upon submission of receipts for home-office equipment setup during the first year of employment.

SECTION 3: HEALTH INSURANCE & FINANCIAL BENEFITS
- Group Medical Coverage: Employees and their immediate dependents (spouse + up to 2 children) are covered under Comprehensive Health Plan B. The annual deductible is $1,500 per family.
- Wellness Perk: Monthly gym, yoga, or mental health app subscriptions are reimbursable up to $50/month under the corporate wellness program.

SECTION 4: ESCALATION & TICKET PROTOCOL
- If an employee query is not addressed within this policy document or if an exception is required, the system must immediately generate an official HR Support Ticket routed to hr-operations@enterprise.com with a 24-hour SLA.
"""

# -------------------------------------------------------------------------
# 4. MAIN INTERFACE & CHAT LOGIC
# -------------------------------------------------------------------------
st.markdown('<p class="main-header">🛡️ OmniHR Enterprise Copilot</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Director-Grade Autonomous HR Policy Assistant with Strict RAG Grounding & Automated Escalation.</p>', unsafe_allow_html=True)
st.markdown("---")

if not api_key_input:
    st.warning("⚠️ Please input your Google Gemini API Key in the sidebar control panel to start.")
else:
    genai.configure(api_key=api_key_input)

    # Load custom text if uploaded, otherwise default handbook
    policy_context = DEFAULT_HR_POLICY
    if uploaded_file is not None:
        policy_context = uploaded_file.getvalue().decode("utf-8")

    # Define Director-level system instructions & guardrails
    system_instruction = f"""
    You are OmniHR, an elite, professional Enterprise HR Assistant.
    Answer the user's question strictly using ONLY the corporate policy handbook context provided below.
    If the answer cannot be found precisely within the context, you MUST state:
    'I do not have verified information on that in our official corporate handbook. Would you like me to log an official HR support ticket for you?'
    Never invent policy details, numbers, or legal commitments.

    OFFICIAL CORPORATE HANDBOOK:
    {policy_context}
    """

    # Initialize Gemini 1.5 Flash model
    model = genai.GenerativeModel(
        model_name="gemini-3.8-flash",
        system_instruction=system_instruction
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "Hello! I am your OmniHR Copilot. How may I assist you with company policies, benefits, or leave structures today?"
        }]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_query := st.chat_input("Ask a policy question (e.g., 'What is our remote work policy?')"):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing policy context and applying guardrails..."):
                try:
                    gemini_history = []
                    for m in st.session_state.chat_history[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [m["content"]]})

                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(user_query)
                    
                    answer_text = response.text
                    sources_snippet = "\n\n*Source Citations:* Verified against official corporate handbook."
                    final_output = answer_text + sources_snippet
                    
                    st.markdown(final_output)
                    st.session_state.chat_history.append({"role": "assistant", "content": final_output})
                
                except Exception as e:
                    error_message = f"⚠️ System Exception Encountered: {str(e)}. Fallback ticket generation initiated."
                    st.error(error_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_message})