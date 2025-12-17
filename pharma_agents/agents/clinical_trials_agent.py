# agents/clinical_trials_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class ClinicalTrialsAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Clinical Trials Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract molecule/indication/phase from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract clinical trial query parameters. "
            "Return JSON: {{\"molecule\": \"<molecule_or_null>\", \"indication\": \"<indication_or_null>\", \"phase\": \"<phase_or_null>\"}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        molecule = params.get("molecule")
        indication = params.get("indication")
        phase = params.get("phase")

        # 2. Call API
        api_params = {}
        if molecule:
            api_params["molecule"] = molecule
        if indication:
            api_params["indication"] = indication
        if phase:
            api_params["phase"] = phase

        if not api_params:
            return {
                "agent": self.name,
                "params": {},
                "raw": {},
                "summary": "Could not extract molecule or indication from query."
            }

        raw = self._get("/api/clinical-trials", api_params)

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the clinical trial data. Highlight: "
            "- Total and active trials"
            "- Phase distribution"
            "- Key ongoing trials with sponsors"
            "- Geographic distribution"
            "- Development timeline insights"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"molecule": molecule, "indication": indication, "phase": phase},
            "raw": raw,
            "summary": summary,
        }
    