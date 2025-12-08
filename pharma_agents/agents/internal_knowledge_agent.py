# agents/internal_knowledge_agent.py

from typing import Any, Dict, Optional
import requests

from .base_agent import BaseAgent


class InternalKnowledgeAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Internal Knowledge Agent"

    def run(
        self,
        document_type: Optional[str] = None,
        topic: Optional[str] = None,
        search_query: Optional[str] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        """
        Calls /api/internal-knowledge with optional filters.
        """
        url = f"{self.base_url}/api/internal-knowledge"
        params: Dict[str, Any] = {}
        if document_type:
            params["document_type"] = document_type
        if topic:
            params["topic"] = topic
        if search_query:
            params["search_query"] = search_query

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "query": {
                "document_type": document_type,
                "topic": topic,
                "search_query": search_query,
            },
            "raw": data,
        }