import os
from models.rag_engine import RAGEngine
from models.voice_engine import VoiceEngine
from models.llm_engine import LLMEngine

class AgentController:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.voice_engine = VoiceEngine()
        self.llm_engine = LLMEngine()

    def add_document(self, file_path):
        """Adds a document to the RAG knowledge base."""
        return self.rag_engine.process_file(file_path)

    def process_voice_input(self, audio_file_path):
        """
        Orchestrates the voice-to-voice flow:
        1. Transcribe audio to text.
        2. Retrieve context from RAG.
        3. Generate LLM response.
        4. Convert response to audio.
        """
        # 1. Transcribe
        transcript = self.voice_engine.transcribe(audio_file_path)
        
        # 2. Retrieve
        context = self.rag_engine.query(transcript)
        
        # 3. Generate
        response_text = self.llm_engine.generate_response(transcript, context)
        
        # 4. Speak
        audio_response_path = self.voice_engine.speak(response_text)
        
        return {
            "transcript": transcript,
            "response": response_text,
            "audio_path": audio_response_path
        }

    def process_text_input(self, text):
        """Processes text input with RAG context."""
        context = self.rag_engine.query(text)
        response_text = self.llm_engine.generate_response(text, context)
        return response_text
