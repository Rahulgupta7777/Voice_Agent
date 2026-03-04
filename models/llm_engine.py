import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are a helpful Voice AI Assistant. You will be provided with context retrieved from a knowledge base.
        Use the provided context to answer the user's question accurately and concisely.
        If the answer is not in the context, say you don't know based on the provided documents.
        Keep your response brief as it will be read aloud.
        """

    def generate_response(self, query, context=""):
        """Generates a response using GPT-4o-mini with RAG context."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
