# agents/clinical_trials_agent.py

from typing import Any, Dict, Optional
import requests

from .base_agent import BaseAgent


class ClinicalTrialsAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Clinical Trials Agent"

    def run(
        self,
        molecule: Optional[str] = None,
        indication: Optional[str] = None,
        phase: Optional[str] = None,
        **_: Any,
    ) -> Dict[str, Any]:
        """
        Calls /api/clinical-trials?molecule=...&indication=...&phase=...
        """
        url = f"{self.base_url}/api/clinical-trials"
        params: Dict[str, Any] = {}
        if molecule:
            params["molecule"] = molecule
        if indication:
            params["indication"] = indication
        if phase:
            params["phase"] = phase

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "agent": self.name,
            "query": {
                "molecule": molecule,
                "indication": indication,
                "phase": phase,
            },
            "raw": data,
        }