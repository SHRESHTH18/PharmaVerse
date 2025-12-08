# agents/iqvia_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class IQVIAAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "IQVIA Insights Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract molecule from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract the molecule name from the query. "
            "Return JSON: {{\"molecule\": \"<molecule_name>\"}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        molecule = params.get("molecule", "").strip()
        
        if not molecule:
            return {
                "agent": self.name,
                "params": {},
                "raw": {},
                "summary": "Could not extract molecule name from query."
            }

        # 2. Call API
        raw = self._get("/api/iqvia", {"molecule": molecule})

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the IQVIA market data. Highlight: "
            "- Market size and growth (CAGR)"
            "- Top markets by sales"
            "- Competition landscape"
            "- Unmet needs"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"molecule": molecule},
            "raw": raw,
            "summary": summary,
        }
