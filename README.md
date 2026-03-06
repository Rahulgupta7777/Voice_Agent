# EchoMind AI - Voice AI Agent with RAG

EchoMind AI is a functional Voice AI Agent that can "listen" to a user's question, "read" from a provided knowledge base (PDF/Text), and "speak" back the answer. The system prioritizes low latency to ensure the conversation feels natural.

## Features

- **STT (Speech-to-Text):** Converts live microphone input to text using OpenAI Whisper.
- **RAG Engine:** Indexes documents (PDF/Text) and retrieves relevant context using LangChain and FAISS.
- **Orchestration:** Handles the flow and prompt grounding with GPT-4o-mini.
- **TTS (Text-to-Speech):** Converts the LLM's response back to audio using OpenAI TTS.
- **MVC Architecture:** Clean separation of concerns for maintainability.
- **Streamlit UI:** A premium, responsive dashboard for a great user experience.

##  Tech Stack

- **Frontend:** Streamlit
- **LLM/STT/TTS:** OpenAI API
- **Vector Store:** FAISS
- **Retrieval:** LangChain

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Rahulgupta7777/Voice_Agent.git
    cd Voice_Agent
    ```

2. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Setup environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:

    ```env
    DEEPGRAM_API_KEY-your_deepgram_api_key_here
    ```

## Use

1. **Run the application:**

    ```bash
    streamlit run app.py
    ```

2. **Upload documents:** Use the sidebar to upload PDF or TXT files to build your knowledge base.
3. **Interact:** Hold the recording button to ask a question via voice, or use the text input.

## Project Structure

- `models/`: RAG, Voice, and LLM core logic.
- `controllers/`: Orchestration logic.
- `app.py`: Streamlit interface.
- `data/`: Temporary storage for indexed documents 
