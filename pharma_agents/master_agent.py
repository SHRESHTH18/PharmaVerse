# master_agent.py

from typing import Any, Dict, List, Optional

from config import settings
from agents.iqvia_agent import IQVIAAgent
from agents.exim_agent import EXIMAgent
from agents.patent_agent import PatentAgent
from agents.clinical_trials_agent import ClinicalTrialsAgent
from agents.internal_knowledge_agent import InternalKnowledgeAgent
from agents.web_intel_agent import WebIntelligenceAgent
from agents.report_agent import ReportAgent


class MasterAgent:
    """
    Conversation orchestrator for Problem Statement 1.

    For now this is *not* LLM-based; it just orchestrates calls based on
    molecule + indication inputs.
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        api_base = base_url or settings.api_base_url

        # Instantiate worker agents
        self.iqvia_agent = IQVIAAgent(api_base)
        self.exim_agent = EXIMAgent(api_base)
        self.patent_agent = PatentAgent(api_base)
        self.ct_agent = ClinicalTrialsAgent(api_base)
        self.internal_agent = InternalKnowledgeAgent(api_base)
        self.web_agent = WebIntelligenceAgent(api_base)
        self.report_agent = ReportAgent(api_base)

    def evaluate_molecule(
        self,
        molecule: str,
        indication: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        High-level orchestration for:
        - molecule
        - optional indication

        Returns a dictionary with all worker responses and the final report metadata.
        """

        # 1. Market + EXIM + patents + clinical + internal + web
        iqvia_result = self.iqvia_agent.run(molecule=molecule)
        exim_result = self.exim_agent.run(product=f"{molecule} API")
        patent_result = self.patent_agent.run(molecule=molecule, indication=indication)
        ct_result = self.ct_agent.run(molecule=molecule, indication=indication)
        internal_result = self.internal_agent.run(topic=f"{molecule} strategy")
        web_result = self.web_agent.run(
            query=f"{molecule} {indication or ''} clinical guidelines"
        )

        # 2. Simple “summary” fields (no LLM, just picking key data to illustrate)
        market_summary = iqvia_result.get("raw", {})
        patent_summary = patent_result.get("raw", {})
        clinical_summary = ct_result.get("raw", {})

        # 3. Decide sections for the report
        include_sections: List[str] = [
            "Executive Summary",
            "Market Analysis",
            "EXIM / Sourcing",
            "Clinical Pipeline",
            "Patent Landscape",
            "Internal Strategy Insights",
            "Guidelines & Web Intelligence",
            "Recommendations",
        ]

        # 4. Generate report via report agent
        topic = f"Innovation Opportunity Assessment for {molecule} ({indication or 'General'})"
        report_result = self.report_agent.run(
            report_type="pdf",
            topic=topic,
            include_sections=include_sections,
        )

        # 5. Aggregate everything
        return {
            "query": {
                "molecule": molecule,
                "indication": indication,
            },
            "results": {
                "iqvia": iqvia_result,
                "exim": exim_result,
                "patents": patent_result,
                "clinical_trials": ct_result,
                "internal_knowledge": internal_result,
                "web_intelligence": web_result,
                "report": report_result,
            },
            "simple_summary": {
                "market_summary": market_summary,
                "patent_summary": patent_summary,
                "clinical_summary": clinical_summary,
            },
        }