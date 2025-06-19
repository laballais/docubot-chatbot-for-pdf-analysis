import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

# Load API key securely
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Default LLM settings. You may change this
DEFAULT_LLM_SETTINGS = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500
}

def get_llm_settings(session_state):
    """Fetch LLM settings from session_state or use defaults."""
    if "llm_settings" not in session_state:
        session_state.llm_settings = DEFAULT_LLM_SETTINGS
    return session_state.llm_settings

def update_llm(session_state):
    """Update LLM instance in session state with new settings."""
    llm_settings = get_llm_settings(session_state)
    session_state.llm = ChatOpenAI(
        model_name=llm_settings["model"],
        temperature=llm_settings["temperature"],
        max_tokens=llm_settings["max_tokens"],
        openai_api_key=openai_api_key
    )

def configure_llm_sidebar(st, session_state):
    """Create LLM settings UI in the sidebar."""
    st.sidebar.markdown("### 🔹 **LLM Settings**")

    model = st.selectbox("Model:", ["gpt-3.5-turbo", "gpt-4"], index=["gpt-3.5-turbo", "gpt-4"].index(get_llm_settings(session_state)["model"]))
    temperature = st.slider("Temperature:", 0.0, 1.0, get_llm_settings(session_state)["temperature"], 0.1)
    max_tokens = st.number_input("Max Tokens:", 100, 2000, get_llm_settings(session_state)["max_tokens"], 50)

    if st.button("Config LLM", use_container_width=True):
        session_state.llm_settings = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        update_llm(session_state)
        st.success("LLM settings successfully configured!")
        st.rerun()
