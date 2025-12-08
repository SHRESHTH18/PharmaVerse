# agents/exim_agent.py

from typing import Any, Dict, Optional
import requests

from .base_agent import BaseAgent


class EXIMAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "EXIM Trends Agent"

    def run(
        self,
        product: str,
        country: Optional[str] = None,
        year: int = 2024,
        **_: Any,
    ) -> Dict[str, Any]:
        """
        Calls /api/exim?product=...&country=...&year=...
        """
        url = f"{self.base_url}/api/exim"
        params = {"product": product, "year": year}
        if country:
            params["country"] = country

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "product": product,
            "country": country,
            "year": year,
            "raw": data,
        }