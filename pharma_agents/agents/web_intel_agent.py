# agents/web_intel_agent.py

from typing import Any, Dict, Optional
import requests

from .base_agent import BaseAgent


class WebIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Web Intelligence Agent"

    def run(self, query: str, source_type: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        """
        Calls /api/web-intelligence?query=...&source_type=...
        """
        url = f"{self.base_url}/api/web-intelligence"
        params: Dict[str, Any] = {"query": query}
        if source_type:
            params["source_type"] = source_type

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "query": query,
            "source_type": source_type,
            "raw": data,
        }