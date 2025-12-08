# agents/report_agent.py
from typing import Any, Dict, List, Optional
import json
from .base_agent import BaseAgent


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
        include_sections: Optional[List[str]] = None,
        report_type: str = "pdf",
    ) -> Dict[str, Any]:
        """
        Generates a report with all detailed agent data.
        """
        # Prepare detailed report data
        report_data = {
            "user_query": user_query,
            "plan": plan,
            "worker_results": worker_results,
            "detailed_agent_responses": []
        }
        
        # Collect all detailed agent data
        for result in worker_results:
            agent_data = {
                "agent_name": result.get("agent", "unknown"),
                "params": result.get("params", {}),
                "summary": result.get("summary", ""),
                "raw_json_response": result.get("raw", {})
            }
            report_data["detailed_agent_responses"].append(agent_data)
        
        # Call API with report data
        params = {
            "report_type": report_type,
            "topic": topic,
        }
        if include_sections:
            params["include_sections"] = include_sections

        # Send report_data in POST body
        raw = self._post("/api/generate-report", params, json_data=report_data)

        return {
            "agent": self.name,
            "topic": topic,
            "report_type": report_type,
            "raw": raw,
        }

    def _post(self, path: str, params: Dict[str, Any], json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Override to support sending JSON data in body"""
        import requests
        url = f"{self.base_url}{path}"
        if json_data:
            response = requests.post(url, params=params, json=json_data, timeout=30)
        else:
            response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
