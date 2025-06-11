import os
import json
import datetime

CHAT_HISTORY_DIR = "chat_histories"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def get_timestamped_session():
    """Generate a timestamped session name."""
    return datetime.datetime.now().strftime("Session_%Y-%m-%d_%H-%M-%S")

def list_chat_sessions():
    """List all available chat sessions."""
    return sorted([f.replace(".json", "") for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")], reverse=True)

def load_chat_history(session_name):
    """Load chat history for the given session."""
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{session_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get("messages", []), data.get("document_texts", []), data.get("uploaded_file_names", [])
    return [], [], []

def save_chat_history(session_name, messages, document_texts, uploaded_file_names=[]):
    """Save chat history to a file."""
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{session_name}.json")
    with open(file_path, "w") as file:
        json.dump({"messages": messages, "document_texts": document_texts, "uploaded_file_names": uploaded_file_names}, file)

def manage_sessions(st, session_state):
    """Create UI elements for managing chat sessions."""
    st.sidebar.markdown("### 🔹 **Chat Sessions**")
    
    session_names = list_chat_sessions()
    selected_session = st.selectbox("Select a chat session:", session_names)

    if selected_session and selected_session != session_state.get("current_session"):
        session_state.current_session = selected_session
        session_state.messages, session_state.document_texts, session_state.uploaded_file_names = load_chat_history(selected_session)
        st.rerun()

    if st.button("Create New Chat", use_container_width=True):
        session_state.current_session = get_timestamped_session()
        session_state.messages = []
        session_state.document_texts = []
        session_state.uploaded_file_names = []
        save_chat_history(session_state.current_session, [], [], [])
        st.rerun()

    if st.button("Delete Current Chat", use_container_width=True):
        session_file = os.path.join(CHAT_HISTORY_DIR, f"{session_state.current_session}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
        session_state.current_session = None
        session_state.messages = []
        session_state.document_texts = []
        session_state.uploaded_file_names = []
        st.rerun()

    if st.button("Clear All Chat Sessions", use_container_width=True):
        for file in os.listdir(CHAT_HISTORY_DIR):
            if file.endswith(".json"):
                os.remove(os.path.join(CHAT_HISTORY_DIR, file))
        session_state.current_session = None
        session_state.messages = []
        session_state.document_texts = []
        session_state.uploaded_file_names = []
        st.rerun()
