import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_core.tools import tool
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

@tool
def get_current_date_time(query: str = "") -> str:
    """Useful for when you need to answer questions about the current date, time, or what day it is today. Input can be empty."""
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%A, %B %d, %Y %I:%M %p")

class LLMEngine:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.search_tool = DuckDuckGoSearchRun()
        self.tools = [self.search_tool, get_current_date_time]
        
        system_prompt = """
        You are EchoMind AI, a highly conversational, friendly, and helpful voice assistant.
        You have access to the internet to answer real-time questions about geopolitics, news, facts, etc., and you know the current date and time.
        You may be provided with context retrieved from a user-uploaded knowledge base. Focus on using it if it exists.
        Keep your responses reasonably brief, engaging, and easy to be read aloud (e.g. avoid complex markdown formatting, bullet points or URLs).
        """
        
        self.agent = create_react_agent(self.llm, self.tools, prompt=system_prompt)

    def generate_response(self, query, context=""):
        """Generates a response using GPT-4o-mini with RAG context and internet search capabilities."""
        if context:
            full_query = f"Context from uploaded docs: {context}\n\nUser Question: {query}"
        else:
            full_query = query
        
        try:
            response = self.agent.invoke({"messages": [("user", full_query)]})
            return response["messages"][-1].content
        except Exception as e:
            try:
                fallback = self.llm.invoke(full_query)
                return fallback.content
            except Exception:
                return f"I encountered an error processing that: {str(e)}"
