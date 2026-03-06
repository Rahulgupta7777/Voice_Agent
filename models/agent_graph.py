import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from models.rag_engine import RAGEngine
from models.voice_engine import VoiceEngine
from models.llm_engine import LLMEngine

class AgentState(TypedDict):
    input_text: str
    input_audio_path: str
    context: str
    output_text: str
    output_audio_path: str
    has_audio_input: bool

class AgentGraph:
    def __init__(self, rag_engine: RAGEngine, voice_engine: VoiceEngine, llm_engine: LLMEngine):
        self.rag_engine = rag_engine
        self.voice_engine = voice_engine
        self.llm_engine = llm_engine
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("transcribe", self.transcribe_node)
        workflow.add_node("retrieve", self.retrieve_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("synthesize", self.synthesize_node)
        
        # Add conditional edges
        workflow.set_conditional_entry_point(
            self.route_start,
            {
                "transcribe": "transcribe",
                "retrieve": "retrieve"
            }
        )
        
        workflow.add_edge("transcribe", "retrieve")
        workflow.add_edge("retrieve", "generate")
        
        workflow.add_conditional_edges(
            "generate",
            self.route_end,
            {
                "synthesize": "synthesize",
                "end": END
            }
        )
        
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()

    def route_start(self, state: AgentState):
        if state.get("has_audio_input", False):
            return "transcribe"
        return "retrieve"

    def route_end(self, state: AgentState):
        return "synthesize"

    def transcribe_node(self, state: AgentState):
        audio_path = state.get("input_audio_path")
        transcript = self.voice_engine.transcribe(audio_path)
        return {"input_text": transcript}

    def retrieve_node(self, state: AgentState):
        text = state.get("input_text", "")
        context = self.rag_engine.query(text)
        return {"context": context}

    def generate_node(self, state: AgentState):
        query = state.get("input_text", "")
        context = state.get("context", "")
        response_text = self.llm_engine.generate_response(query, context)
        return {"output_text": response_text}

    def synthesize_node(self, state: AgentState):
        import uuid
        text = state.get("output_text", "")
        unique_id = str(uuid.uuid4())
        output_audio_path = self.voice_engine.speak(text, output_path=f"response_{unique_id}.mp3")
        return {"output_audio_path": output_audio_path}

    def invoke(self, input_data: dict):
        return self.graph.invoke(input_data)
