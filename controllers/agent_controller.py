import os
from models.rag_engine import RAGEngine
from models.voice_engine import VoiceEngine
from models.llm_engine import LLMEngine
from models.agent_graph import AgentGraph

class AgentController:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.voice_engine = VoiceEngine()
        self.llm_engine = LLMEngine()
        self.agent_graph = AgentGraph(self.rag_engine, self.voice_engine, self.llm_engine)

    def add_document(self, file_path):
        """Adds a document to the RAG knowledge base."""
        return self.rag_engine.process_file(file_path)

    def process_voice_input(self, audio_file_path):
        """
        Orchestrates the voice-to-voice flow using LangGraph.
        """
        initial_state = {
            "input_audio_path": audio_file_path,
            "has_audio_input": True
        }
        
        # Invoke LangGraph
        final_state = self.agent_graph.invoke(initial_state)
        
        return {
            "transcript": final_state.get("input_text", ""),
            "response": final_state.get("output_text", ""),
            "audio_path": final_state.get("output_audio_path", "")
        }

    def process_text_input(self, text):
        """Processes text input with RAG context using LangGraph."""
        initial_state = {
            "input_text": text,
            "has_audio_input": False
        }
        
        # Invoke LangGraph
        final_state = self.agent_graph.invoke(initial_state)
        return {
            "response": final_state.get("output_text", ""),
            "audio_path": final_state.get("output_audio_path", "")
        }
