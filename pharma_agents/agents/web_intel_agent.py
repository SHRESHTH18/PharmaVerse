# agents/web_intel_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class WebIntelligenceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Web Intelligence Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract search query and source_type from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract web intelligence query parameters. "
            "Create a concise search query and optionally specify source_type. "
            "Return JSON: {{\"query\": \"<search_query>\", \"source_type\": \"<guidelines|publications|news|patient_forums|null>\"}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        query = params.get("query", "").strip()
        source_type = params.get("source_type")

        if not query:
            return {
                "agent": self.name,
                "params": {},
                "raw": {},
                "summary": "Could not extract search query from user input."
            }

        # 2. Call API
        api_params = {"query": query}
        if source_type:
            api_params["source_type"] = source_type
        raw = self._get("/api/web-intelligence", api_params)

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the web intelligence findings. Highlight: "
            "- Key guidelines and recommendations"
            "- Important publications"
            "- Relevant news"
            "- Patient forum insights and sentiment"
            "- Credibility and source quality"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"query": query, "source_type": source_type},
            "raw": raw,
            "summary": summary,
        }
