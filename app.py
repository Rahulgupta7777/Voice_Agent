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
    /* Hide top header and footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 900px !important;
    }
    
    .stApp {
        background-color: #0b101a;
        color: #e6edf3;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* General Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        color: white;
    }
    
    /* Chat Layout */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 20px;
    }
    
    .row-user {
        justify-content: flex-end;
    }
    
    .row-assistant {
        justify-content: flex-start;
    }
    
    .chat-bubble {
        padding: 16px 20px;
        border-radius: 20px;
        max-width: 80%;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        font-size: 16px;
        line-height: 1.5;
        animation: fadeIn 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) forwards;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-bubble {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #f8fafc;
        border-bottom-left-radius: 4px;
    }
    
    .header-text {
        text-align: center;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -1px;
    }
    
    .subtitle {
        text-align: center; 
        color: #94a3b8; 
        font-size: 1.15rem;
        margin-bottom: 2.5rem;
    }
    
    /* Improve scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
    
    /* Text Input Styling */
    .stTextInput>div>div>input {
        border-radius: 12px;
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
        padding: 12px 18px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 1px #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Controller ---
if 'controller' not in st.session_state:
    st.session_state.controller = AgentController()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []

import base64

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    
    st.subheader("📚 Knowledge Base")
    st.markdown("Upload documents for EchoMind to reference in conversation.")
    uploaded_files = st.file_uploader("Upload PDF or TXT files", type=['pdf', 'txt'], accept_multiple_files=True, label_visibility="collapsed")
    
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

    if st.session_state.processed_docs:
        st.markdown("**Active Documents:**")
        for doc in st.session_state.processed_docs:
            st.markdown(f"📄 `{doc}`")
    
    st.markdown("---")
    if st.button("🗑️ Clear Memory & Chat", use_container_width=True):
        st.session_state.controller.rag_engine.clear()
        st.session_state.processed_docs = []
        st.session_state.chat_history = []
        st.rerun()

# --- Main Page ---
st.markdown('<h1 class="header-text">EchoMind AI</h1>', unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your intelligent, conversational voice assistant.</p>", unsafe_allow_html=True)

# --- Chat Display ---
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.markdown("<div style='text-align: center; padding: 60px; color: #64748b; font-size: 17px;'><em>No conversation yet. Hold the mic button below to start talking!</em></div>", unsafe_allow_html=True)
    
    for idx, chat in enumerate(st.session_state.chat_history):
        if chat["role"] == "user":
            st.markdown(f'''
            <div class="chat-row row-user">
                <div class="chat-bubble user-bubble">
                    🗣️ <strong>You</strong><br><br>{chat["content"]}
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            # Inline audio player directly in the bubble
            audio_html = ""
            if "audio" in chat:
                try:
                    with open(chat["audio"], "rb") as f:
                        b64 = base64.b64encode(f.read()).decode()
                        is_latest = (idx == len(st.session_state.chat_history) - 1)
                        autoplay = 'autoplay="true"' if is_latest else ''
                        audio_html = f'<br><br><audio controls {autoplay} style="height: 36px; border-radius: 18px; width: 240px; outline: none; box-shadow: 0 4px 12px rgba(0,0,0,0.3);"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                except Exception as e:
                    print(e)
                    pass
                    
            st.markdown(f'''
            <div class="chat-row row-assistant">
                <div class="chat-bubble assistant-bubble">
                    ✨ <strong>EchoMind</strong><br><br>{chat["content"]}{audio_html}
                </div>
            </div>
            ''', unsafe_allow_html=True)

st.markdown("<br><hr style='border: 1px solid rgba(255,255,255,0.05); margin: 20px 0 30px 0;'><br>", unsafe_allow_html=True)

# --- Bottom Input Area ---
st.markdown("<br><br>", unsafe_allow_html=True)

# Restrict the width significantly to make it look like a sleek AI chat bar
spacer_l, center_col, spacer_r = st.columns([1, 2.5, 1])

with center_col:
    # Center the Mic Button more deeply
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        audio = mic_recorder(
            start_prompt="🎙️ Press & Hold to Talk",
            stop_prompt="⏹️ Release to Send",
            just_once=True
        )

    if audio:
        with st.spinner("Processing your voice..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(audio['bytes'])
                tmp_audio_path = tmp_audio.name
            
            result = st.session_state.controller.process_voice_input(tmp_audio_path)
            
            st.session_state.chat_history.append({"role": "user", "content": result["transcript"]})
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": result["response"],
                "audio": result["audio_path"]
            })
            
            os.unlink(tmp_audio_path)
            st.rerun()

    st.markdown("<div style='text-align: center; color: #475569; font-size: 13px; margin: 15px 0 10px 0;'>— OR QUICK TYPE —</div>", unsafe_allow_html=True)
    
    # Text input perfectly centered below the mic button
    text_input = st.text_input("Ask a question", label_visibility="collapsed", placeholder="Message EchoMind...")
    
    if st.button("Send Message ➤", use_container_width=True):
        if text_input:
            with st.spinner("EchoMind is thinking..."):
                response = st.session_state.controller.process_text_input(text_input)
                st.session_state.chat_history.append({"role": "user", "content": text_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

# --- Extra Footer Padding to avoid cutting off at bottom ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
