# agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_client import GroqLLM
from langchain.prompts import ChatPromptTemplate


class BaseAgent(ABC):
    """Abstract base class for all Worker Agents with LLM capabilities."""

    def __init__(self, base_url: str, llm: Optional[GroqLLM] = None) -> None:
        # Base URL of the mock API server
        self.base_url = base_url.rstrip("/")
        # LLM for parsing queries and generating responses
        self.llm = llm or GroqLLM()

    @property
    @abstractmethod
    def name(self) -> str:
        """Human readable name for the agent."""
        raise NotImplementedError

    def _parse_query_with_llm(self, user_query: str, extraction_prompt: str) -> Dict[str, Any]:
        """Use LLM to parse the user query and extract parameters"""
        system_prompt = (
            f"You are an intelligent query parser for the {self.name}. "
            "Extract relevant parameters from the user query. "
            "Return ONLY valid JSON, no explanation or commentary."
        )
        
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{extraction_prompt}\n\nUser query: {user_query}\n\nReturn ONLY valid JSON.")
        ])
        
        messages = template.format_messages(
            extraction_prompt=extraction_prompt,
            user_query=user_query
        )
        
        response = self.llm.invoke([(m.type, m.content) for m in messages])
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                return json.loads(response[start:end])
            except:
                return {}

    def _generate_summary_with_llm(self, json_response: Dict[str, Any], summary_prompt: str) -> str:
        """Use LLM to generate a summary from JSON response"""
        system_prompt = (
            f"You are an intelligent analyst for the {self.name}. "
            "Analyze the JSON data and provide a clear, concise summary."
        )
        
        user_prompt = f"{summary_prompt}\n\nJSON Response:\n{json.dumps(json_response, indent=2)}"
        
        return self.llm.chat(system_prompt, user_prompt)

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method for GET requests"""
        url = f"{self.base_url}{path}"
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method for POST requests"""
        url = f"{self.base_url}{path}"
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    @abstractmethod
    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Execute this agent's main function.
        
        Each agent should:
        1. Use LLM to parse user_query and extract parameters
        2. Call the appropriate API endpoint
        3. Get JSON response
        4. Use LLM to generate summary from JSON
        5. Return agent name, params, raw JSON, and summary
        """
        raise NotImplementedError
