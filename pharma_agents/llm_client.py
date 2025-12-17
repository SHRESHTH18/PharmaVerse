# llm_client.py
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class GroqLLM:
    """Wrapper for Groq LLM using LangChain"""
    
    def __init__(self, model_name: str = "llama-3.1-8b-instant", temperature: float = 0.7):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.model_name = model_name
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Simple chat interface with system and user prompts"""
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content
    
    def invoke(self, messages: list) -> str:
        """Invoke with message list format"""
        response = self.llm.invoke(messages)
        return response.content

