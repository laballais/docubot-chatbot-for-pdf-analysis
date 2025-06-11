import pdfplumber
import streamlit as st
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from llm_config import configure_llm_sidebar, update_llm
from session_manager import manage_sessions, load_chat_history, save_chat_history, get_timestamped_session

# Initialize LLM settings before using it
update_llm(st.session_state)

# Streamlit UI Title
st.set_page_config(page_title="DocuBot", page_icon="📄")
st.title("DocuBot: Chatbot for PDF Analysis")

# Sidebar for LLM and Session Management
with st.sidebar:
    manage_sessions(st, st.session_state)
    configure_llm_sidebar(st, st.session_state)

# Ensure session state variables are initialized
if "current_session" not in st.session_state or not st.session_state.current_session:
    st.session_state.current_session = get_timestamped_session()

st.session_state.messages, st.session_state.document_texts, st.session_state.uploaded_file_names = load_chat_history(st.session_state.current_session)

# Multi-file uploader with session-specific key
uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, key=f"file_uploader_{st.session_state.current_session}")

if uploaded_files:
    document_texts = []
    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            text = " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            if not text.strip():
                st.warning(f"Could not extract text from {uploaded_file.name}")
            document_texts.append(text)

    # Store extracted text and filenames
    st.session_state.document_texts = document_texts
    st.session_state.uploaded_file_names = [file.name for file in uploaded_files]
    save_chat_history(st.session_state.current_session, st.session_state.messages, document_texts, st.session_state.uploaded_file_names)

# Display uploaded files
if st.session_state.get("uploaded_file_names"):
    st.write("**Uploaded Reference Files:**")
    for file_name in st.session_state.uploaded_file_names:
        st.write(f"- {file_name}")

# Display previous chat messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["text"])

# Chat input for user questions
user_input = st.chat_input("Ask a question about the documents:")

if user_input:
    if not st.session_state.get("document_texts"):
        st.warning("Please upload PDFs before asking questions.")
    else:
        st.session_state.messages.append({"role": "user", "text": user_input})
        st.chat_message("user").write(user_input)

        # VectorDB query
        combined_text = "\n\n".join(st.session_state.document_texts)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = splitter.split_text(combined_text)

        if texts:  # Ensure texts exist before vector embedding
            vector_db = Chroma.from_texts(texts, OpenAIEmbeddings())
            relevant_text = " ".join([doc.page_content for doc in vector_db.similarity_search(user_input, k=2)])
            # response = st.session_state.llm.predict(f"Context: {relevant_text}\nQuestion: {user_input}")
            response = st.session_state.llm.predict(
                            f"""
                            You are a document analysis assistant. Given the document, format your response **clearly and neatly**.

                            Context: {relevant_text}

                            Question: {user_input}

                            Make your answer **clear, concise, and fact-based**.
                            
                            Use a uniform font for your response so the reponse is readable. Manually put spaces between words where needed.
                             
                            If the document doesn't contain relevant information, say so.
                            
                            If the answer contains numerical data, output a well-structured table with headers.

                            If summarizing, provide a **brief, well-structured overview** with key bullet points.

                            If this question **relates to a previous query**, reference past responses before answering.
    
                            If clarification is needed, politely ask the user before responding.
                            """
                        )
        else:
            response = "No relevant text found in uploaded PDFs."

        st.session_state.messages.append({"role": "assistant", "text": response})
        st.chat_message("assistant").write(response)

        save_chat_history(st.session_state.current_session, st.session_state.messages, st.session_state.document_texts, st.session_state.uploaded_file_names)
