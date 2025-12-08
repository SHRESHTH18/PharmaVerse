# agents/report_agent.py

from typing import Any, Dict, List, Optional
import requests

from .base_agent import BaseAgent


class ReportAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Report Generator Agent"

    def run(
        self,
        report_type: str,
        topic: str,
        include_sections: Optional[List[str]] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        """
        Calls POST /api/generate-report
        """
        url = f"{self.base_url}/api/generate-report"
        params: Dict[str, Any] = {
            "report_type": report_type,
            "topic": topic,
        }
        if include_sections:
            params["include_sections"] = include_sections

        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "topic": topic,
            "report_type": report_type,
            "raw": data,
        }