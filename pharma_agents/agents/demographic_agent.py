



## ✅ FINAL, PRODUCTION-SAFE `demographic_agent.py`

### 🔁 REPLACE YOUR FILE WITH THIS


# agents/demographic_agent.py
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
import json
import re


class DemographicAgent(BaseAgent):
    """
    Converts worker agent outputs into chart-ready demographic data.
    This agent MUST NEVER crash the pipeline.
    """

    @property
    def name(self) -> str:
        return "Demographic Agent"

    def run(self, worker_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        system_prompt = (
            "You are a Demographics & Data Visualization expert.\n"
            "You will be given raw JSON outputs from pharma intelligence agents.\n\n"
            "STRICT RULES:\n"
            "• Return ONLY valid JSON\n"
            "• No markdown\n"
            "• No explanation\n"
            "• No prose\n\n"
            "IMPORTANT RULES:"
        "- 'values' MUST be numeric (int or float)"
        "- NEVER use strings like 'Expired', 'Active', '%'"
        "- Convert statuses into numeric counts (e.g., expired=1, active=0)"
        "- If data is non-numeric, DO NOT create a chart"
            "Required JSON schema:\n"
            "{\n"
            '  "agents": {\n'
            '    "<Agent Name>": [\n'
            "      {\n"
            '        "id": "string",\n'
            '        "title": "string",\n'
            '        "recommended_chart": "pie | bar | line | donut",\n'
            '        "insight": "string",\n'
            '        "data": {\n'
            '          "labels": [string],\n'
            '          "values": [number],\n'
            '          "unit": "string | null"\n'
            "        }\n"
            "      }\n"
            "    ]\n"
            "  }\n"
            "}"
        )

        user_prompt = (
            "Worker agent outputs:\n\n"
            f"{json.dumps(worker_results, indent=2)}\n\n"
            "Generate demographic charts grouped by agent."
        )

        response = self.llm.chat(system_prompt, user_prompt)

        demographics = self._safe_parse_json(response)

        return {
            "agent": self.name,
            "raw": demographics
        }

    # ------------------------------------------------------------------
    # 🔒 BULLETPROOF JSON PARSER
    # ------------------------------------------------------------------
    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return self._empty_demographics()

        # Remove markdown fences if present
        text = re.sub(r"```json|```", "", text).strip()

        # Extract first JSON object only
        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end <= start:
            return self._empty_demographics()

        json_str = text[start:end]

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return self._empty_demographics()

    def _empty_demographics(self) -> Dict[str, Any]:
        """
        Never crash downstream PDF generation.
        """
        return {
            "agents": {}
        }