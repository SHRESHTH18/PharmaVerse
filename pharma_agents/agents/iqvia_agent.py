# agents/iqvia_agent.py

from typing import Any, Dict
import requests

from .base_agent import BaseAgent


class IQVIAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "IQVIA Insights Agent"

    def run(self, molecule: str, **_: Any) -> Dict[str, Any]:
        """
        Calls /api/iqvia?molecule=...
        """
        url = f"{self.base_url}/api/iqvia"
        params = {"molecule": molecule}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "molecule": molecule,
            "raw": data,
        }