import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = """
        You are EchoMind AI, a highly conversational, friendly, and helpful voice assistant.
        You will be provided with some context retrieved from a knowledge base.
        Use this context to answer the user's questions naturally, as if you are having a conversation with them.
        For example, if the context is a resume, you might say "Oh, I see your resume here! How can I help you with it?"
        If the answer is not in the context, do NOT just say "I don't know based on the provided documents."
        Instead, politely state that you couldn't find it in the documents securely, but you can try to answer based on your general knowledge if they'd like, or steer the conversation naturally.
        Keep your responses reasonably brief, engaging, and easy to be read aloud (e.g. avoid complex markdown formatting, bullet points or URLs).
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
