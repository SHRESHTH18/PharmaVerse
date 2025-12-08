# agents/patent_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class PatentAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Patent Landscape Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract molecule/indication from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract patent query parameters. "
            "Return JSON: {{\"molecule\": \"<molecule_name>\", \"indication\": \"<indication_or_null>\"}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        molecule = params.get("molecule", "").strip()
        indication = params.get("indication")

        if not molecule:
            return {
                "agent": self.name,
                "params": {},
                "raw": {},
                "summary": "Could not extract molecule name from query."
            }

        # 2. Call API
        api_params = {"molecule": molecule}
        if indication:
            api_params["indication"] = indication
        raw = self._get("/api/patents", api_params)

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the patent landscape. Highlight: "
            "- Patent status (active/expired)"
            "- Freedom to Operate (FTO) status"
            "- Key patents and expiry dates"
            "- Generic opportunity assessment"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"molecule": molecule, "indication": indication},
            "raw": raw,
            "summary": summary,
        }
