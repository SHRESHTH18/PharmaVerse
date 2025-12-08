# agents/exim_agent.py
from typing import Any, Dict
from .base_agent import BaseAgent


class EXIMAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "EXIM Trends Agent"

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Uses LLM to extract product/country/year from query, calls API, and generates summary.
        """
        # 1. Parse query with LLM
        extraction_prompt = (
            "Extract EXIM query parameters. "
            "Return JSON: {{\"product\": \"<product_name>\", \"country\": \"<country_or_null>\", \"year\": <year_as_int_or_2024>}}"
        )
        params = self._parse_query_with_llm(user_query, extraction_prompt)
        product = params.get("product", "").strip()
        country = params.get("country")
        year = params.get("year", 2024)

        if not product:
            return {
                "agent": self.name,
                "params": {},
                "raw": {},
                "summary": "Could not extract product name from query."
            }

        # 2. Call API
        api_params = {"product": product, "year": year}
        if country:
            api_params["country"] = country
        raw = self._get("/api/exim", api_params)

        # 3. Generate summary with LLM
        summary_prompt = (
            "Summarize the EXIM trade data. Highlight: "
            "- Export/import volumes by country"
            "- Net trade positions"
            "- Top source/destination countries"
            "- Sourcing risks and dependencies"
        )
        summary = self._generate_summary_with_llm(raw, summary_prompt)

        return {
            "agent": self.name,
            "params": {"product": product, "country": country, "year": year},
            "raw": raw,
            "summary": summary,
        }
