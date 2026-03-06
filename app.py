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
        max-width: 800px !important;
    }
    
    .stApp {
        background-color: #0A0F14;
        color: #e2e8f0;
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* General Button Styling with Glow */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #00d1ff;
        color: #000000;
        border: none;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.25s ease;
        box-shadow: 0 0 12px rgba(0, 209, 255, 0.25);
    }
    .stButton>button:hover {
        background-color: #00bced;
        box-shadow: 0 0 20px rgba(0, 209, 255, 0.45);
        color: #000000;
        transform: translateY(-2px);
    }
    
    /* Secondary button styling (Clear Memory) */
    [data-testid="stSidebar"] .stButton>button {
        background-color: transparent;
        color: #e2e8f0;
        border: 1px solid #283743;
        box-shadow: none;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: #1a242d;
        border-color: #e2e8f0;
        color: #ffffff;
    }
    
    /* Chat Layout */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 28px;
    }
    
    .row-user {
        justify-content: flex-end;
    }
    
    .row-assistant {
        justify-content: flex-start;
    }
    
    .chat-bubble {
        padding: 14px 18px;
        border-radius: 12px;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .user-bubble {
        background-color: #141C24;
        color: #f8fafc;
        border: 1px solid #1f2b36;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .assistant-bubble {
        background-color: transparent;
        color: #e2e8f0;
        border-left: 2px solid #00d1ff;
        border-radius: 0;
        padding-left: 18px;
        margin-left: 4px;
        padding-top: 8px;
        padding-bottom: 8px;
    }
    
    .header-text {
        text-align: center;
        margin-bottom: 4px;
        color: #f1f5f9;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center; 
        color: #64748b; 
        font-size: 1.05rem;
        margin-bottom: 3.5rem;
        font-weight: 400;
    }
    
    /* Improve scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #283743; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3b5062; }
    
    /* Text Input Styling - Sleek Slate */
    .stTextInput>div>div>input {
        border-radius: 8px;
        background-color: #141C24;
        color: #e2e8f0;
        border: 1px solid #1f2b36;
        padding: 14px 16px;
        font-size: 14px;
        transition: all 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #00d1ff;
        box-shadow: 0 0 0 1px #00d1ff;
        background-color: #18222c;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0A0F14;
        border-right: 1px solid #1a242d;
    }
    
    [data-testid="stFileUploader"] {
        background-color: #141C24;
        border-color: #283743;
        border-radius: 10px;
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
st.markdown('<h1 class="header-text">EchoMind <span style="color: #00d1ff;">AI</span></h1>', unsafe_allow_html=True)
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
                     <strong>Asked:</strong><br><br>{chat["content"]}
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
                        audio_html = f'<br><audio controls {autoplay} style="height: 38px; border-radius: 8px; margin-top: 10px; width: 240px; outline: none; opacity: 0.9; color-scheme: dark;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
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
                result = st.session_state.controller.process_text_input(text_input)
                st.session_state.chat_history.append({"role": "user", "content": text_input})
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": result["response"],
                    "audio": result["audio_path"]
                })
                st.rerun()

# --- Extra Footer Padding to avoid cutting off at bottom ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
