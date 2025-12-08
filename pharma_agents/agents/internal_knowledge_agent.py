# agents/internal_knowledge_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class InternalKnowledgeAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Internal Knowledge Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract topic/document_type from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract internal knowledge query parameters. "
            "Return JSON: {{\"topic\": \"<topic_or_null>\", \"document_type\": \"<MINS|Strategy Deck|Field Report|Market Analysis|null>\"}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        topic = params.get("topic")
        document_type = params.get("document_type")

        # 2. Call API
        api_params = {}
        if topic:
            api_params["topic"] = topic
        if document_type:
            api_params["document_type"] = document_type
        api_params["search_query"] = ""

        raw = self._get("/api/internal-knowledge", api_params)

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the internal knowledge documents. Highlight: "
            "- Key takeaways and insights"
            "- Important documents and their dates"
            "- Strategic recommendations"
            "- Market positioning and competitive analysis"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"topic": topic, "document_type": document_type},
            "raw": raw,
            "summary": summary,
        }
