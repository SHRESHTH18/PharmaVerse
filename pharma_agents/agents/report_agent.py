# agents/report_agent.py
from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent
import requests


class ReportAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Report Generator Agent"

    def run(
        self,
        topic: str,
        user_query: str,
        plan: Dict[str, Any],
        worker_results: List[Dict[str, Any]],
        demographics: Dict[str, Any],
        include_sections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        report_data = {
            "topic": topic,
            "user_query": user_query,
            "plan": plan,
            "worker_results": worker_results,
            "demographics": demographics,
            "include_sections": include_sections or [],
            "detailed_agent_responses": [],   # ✅ FIX
        }

        for result in worker_results:
            report_data["detailed_agent_responses"].append({
                "agent_name": result.get("agent", "unknown"),
                "summary": result.get("summary", ""),
                "raw_json_response": result.get("raw", {})
            })

        url = f"{self.base_url}/api/generate-report"

        response = requests.post(
            url,
            json=report_data,
            timeout=60
        )
        response.raise_for_status()

        return {
            "agent": self.name,
            "raw": response.json()
        }