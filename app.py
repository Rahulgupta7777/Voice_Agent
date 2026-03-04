import streamlit as st
import os
import tempfile
from controllers.agent_controller import AgentController
from streamlit_mic_recorder import mic_recorder

# --- Page Config ---
st.set_page_config(
    page_title="EchoMind AI - Your Voice Knowledge Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Design ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        color: white;
    }
    .chat-bubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        max-width: 80%;
    }
    .user-bubble {
        background-color: #2c3e50;
        margin-left: auto;
    }
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-right: auto;
    }
    .header-text {
        text-align: center;
        margin-bottom: 40px;
        background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }
</style>
""", unsafe_allow_index=True)

# --- Initialize Controller ---
if 'controller' not in st.session_state:
    st.session_state.controller = AgentController()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []

# --- Sidebar ---
with st.sidebar:
    st.title("Settings & Knowledge")
    st.markdown("---")
    
    st.subheader("📁 Upload Knowledge Base")
    uploaded_files = st.file_uploader("Upload PDF or TXT files", type=['pdf', 'txt'], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.processed_docs:
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    # Save temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Process in RAG
                    chunks = st.session_state.controller.add_document(tmp_path)
                    st.session_state.processed_docs.append(uploaded_file.name)
                    st.success(f"Indexed {uploaded_file.name} ({chunks} chunks)")
                    os.unlink(tmp_path)

    st.markdown("---")
    st.subheader("📚 Indexed Documents")
    for doc in st.session_state.processed_docs:
        st.write(f"✅ {doc}")
    
    if st.button("Clear Memory"):
        st.session_state.controller.rag_engine.clear()
        st.session_state.processed_docs = []
        st.session_state.chat_history = []
        st.rerun()

# --- Main Page ---
st.markdown('<h1 class="header-text">EchoMind AI</h1>', unsafe_allow_index=True)
st.markdown("<p style='text-align: center; color: #888;'>Your voice-activated knowledge assistant. Listen, Read, Speak.</p>", unsafe_allow_index=True)

# --- Chat Display ---
chat_container = st.container()

with chat_container:
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="chat-bubble user-bubble">🧑‍💻 {chat["content"]}</div>', unsafe_allow_index=True)
        else:
            st.markdown(f'<div class="chat-bubble assistant-bubble">🤖 {chat["content"]}</div>', unsafe_allow_index=True)
            if "audio" in chat:
                st.audio(chat["audio"], format="audio/mp3")

# --- Voice Input ---
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h4 style='text-align: center;'>Hold to Ask</h4>", unsafe_allow_index=True)
    audio = mic_recorder(
        start_prompt="🔴 Start Recording",
        stop_prompt="⏹️ Stop & Process",
        just_once=True,
        use_toggle=False
    )

    if audio:
        with st.spinner("Processing your voice..."):
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(audio['bytes'])
                tmp_audio_path = tmp_audio.name
            
            # Get response from controller
            result = st.session_state.controller.process_voice_input(tmp_audio_path)
            
            # Update history
            st.session_state.chat_history.append({"role": "user", "content": result["transcript"]})
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": result["response"],
                "audio": result["audio_path"]
            })
            
            os.unlink(tmp_audio_path)
            st.rerun()

# --- Fallback Text Input ---
with st.expander("Type your question instead"):
    text_input = st.text_input("Message EchoMind...")
    if st.button("Send Message"):
        if text_input:
            with st.spinner("Thinking..."):
                response = st.session_state.controller.process_text_input(text_input)
                st.session_state.chat_history.append({"role": "user", "content": text_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
