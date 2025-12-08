# agents/patent_agent.py

from typing import Any, Dict, Optional
import requests

from .base_agent import BaseAgent


class PatentAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Patent Landscape Agent"

    def run(self, molecule: str, indication: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        """
        Calls /api/patents?molecule=...&indication=...
        """
        url = f"{self.base_url}/api/patents"
        params = {"molecule": molecule}
        if indication:
            params["indication"] = indication

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "molecule": molecule,
            "indication": indication,
            "raw": data,
        }