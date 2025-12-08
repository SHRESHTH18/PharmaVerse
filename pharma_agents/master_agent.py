# master_agent.py
from typing import Dict, Any, List, TypedDict
import json
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate

from config import settings
from llm_client import GroqLLM
from agents.iqvia_agent import IQVIAAgent
from agents.exim_agent import EXIMAgent
from agents.patent_agent import PatentAgent
from agents.clinical_trials_agent import ClinicalTrialsAgent
from agents.internal_knowledge_agent import InternalKnowledgeAgent
from agents.web_intel_agent import WebIntelligenceAgent
from agents.report_agent import ReportAgent


class AgentState(TypedDict):
    """State for the agent orchestration graph"""
    user_query: str
    plan: Dict[str, Any]
    worker_results: List[Dict[str, Any]]
    final_answer: str
    report: Dict[str, Any]


class MasterAgent:
    """
    Master orchestrator using LangGraph to coordinate worker agents.
    Uses LLM to:
    1. Plan which agents to call
    2. Coordinate agent execution
    3. Generate final summary and actionable steps
    """

    def __init__(self, base_url: str = None) -> None:
        api_base = base_url or settings.api_base_url
        self.llm = GroqLLM()
        
        # Instantiate worker agents
        self.iqvia_agent = IQVIAAgent(api_base, self.llm)
        self.exim_agent = EXIMAgent(api_base, self.llm)
        self.patent_agent = PatentAgent(api_base, self.llm)
        self.ct_agent = ClinicalTrialsAgent(api_base, self.llm)
        self.internal_agent = InternalKnowledgeAgent(api_base, self.llm)
        self.web_agent = WebIntelligenceAgent(api_base, self.llm)
        self.report_agent = ReportAgent(api_base, self.llm)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()

    def _plan_agents(self, state: AgentState) -> AgentState:
        """Use LLM to decide which agents to call and extract molecule/indication"""
        user_query = state["user_query"]
        
        system_prompt = (
            "You are the Master Agent for a pharma innovation evaluation system.\n"
            "Available worker agents:\n"
            "  - iqvia: market size & competition\n"
            "  - exim: API trade & sourcing\n"
            "  - patents: patent landscape & FTO\n"
            "  - clinical: clinical development pipeline\n"
            "  - internal: internal strategy/field insights\n"
            "  - webintel: guidelines, key publications, news, patient forums\n\n"
            "Given a user query, decide which agents are relevant and extract the molecule and indication.\n"
            "Always return STRICT JSON of the form:\n"
            "{{\n"
            '  "molecule": "<molecule or null>",\n'
            '  "indication": "<indication or null>",\n'
            '  "call_iqvia": true/false,\n'
            '  "call_exim": true/false,\n'
            '  "call_patents": true/false,\n'
            '  "call_clinical": true/false,\n'
            '  "call_internal": true/false,\n'
            '  "call_webintel": true/false\n'
            "}}"
        )
        
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "User query:\n{query}\n\nReturn ONLY the JSON object described above.")
        ])
        
        messages = template.format_messages(query=user_query)
        response = self.llm.invoke([(m.type, m.content) for m in messages])
        
        try:
            plan = json.loads(response)
        except json.JSONDecodeError:
            try:
                start = response.find("{")
                end = response.rfind("}") + 1
                plan = json.loads(response[start:end])
            except:
                plan = {
                    "molecule": None,
                    "indication": None,
                    "call_iqvia": True,
                    "call_exim": True,
                    "call_patents": True,
                    "call_clinical": True,
                    "call_internal": True,
                    "call_webintel": True
                }
        
        state["plan"] = plan
        return state

    def _run_workers(self, state: AgentState) -> AgentState:
        """Execute selected worker agents"""
        plan = state["plan"]
        user_query = state["user_query"]
        results: List[Dict[str, Any]] = []

        # Build context for agents
        context = user_query
        if plan.get("molecule"):
            context += f"\nPrimary molecule: {plan['molecule']}"
        if plan.get("indication"):
            context += f"\nPrimary indication: {plan['indication']}"

        # Run selected agents
        if plan.get("call_iqvia"):
            results.append(self.iqvia_agent.run(context))

        if plan.get("call_exim"):
            # For EXIM, add API context if molecule is present
            exim_query = context
            if plan.get("molecule"):
                exim_query += f"\nProduct: {plan['molecule']} API"
            results.append(self.exim_agent.run(exim_query))

        if plan.get("call_patents"):
            results.append(self.patent_agent.run(context))

        if plan.get("call_clinical"):
            results.append(self.ct_agent.run(context))

        if plan.get("call_internal"):
            results.append(self.internal_agent.run(context))

        if plan.get("call_webintel"):
            results.append(self.web_agent.run(context))

        state["worker_results"] = results
        return state

    def _generate_report(self, state: AgentState) -> AgentState:
        """Generate PDF report with all data"""
        plan = state["plan"]
        worker_results = state["worker_results"]
        user_query = state["user_query"]
        
        molecule = plan.get("molecule")
        indication = plan.get("indication")
        topic = (
            f"Innovation Opportunity Assessment for {molecule} ({indication})"
            if molecule and indication
            else f"Innovation Opportunity Assessment - {user_query[:60]}"
        )

        include_sections = [
            "Executive Summary",
            "Market Analysis",
            "EXIM / Sourcing",
            "Clinical Pipeline",
            "Patent Landscape",
            "Internal Strategy Insights",
            "Guidelines & Web Intelligence",
            "Recommendations",
        ]
        
        report_result = self.report_agent.run(
            topic=topic,
            user_query=user_query,
            plan=plan,
            worker_results=worker_results,
            include_sections=include_sections
        )
        
        state["report"] = report_result["raw"]
        return state

    def _generate_final_answer(self, state: AgentState) -> AgentState:
        """Generate final summary and actionable steps"""
        user_query = state["user_query"]
        plan = state["plan"]
        worker_results = state["worker_results"]

        # Build summaries text
        summaries_text = ""
        for r in worker_results:
            summaries_text += f"\n=== {r['agent'].upper()} ===\n{r['summary']}\n"

        system_prompt = (
            "You are the Master Agent for pharma portfolio planning.\n"
            "You will be given:\n"
            "  - The original user query\n"
            "  - A high-level plan (molecule/indication & which agents were used)\n"
            "  - Summaries from worker agents\n\n"
            "Your task:\n"
            "  1. Provide a CONCISE executive summary (2-3 paragraphs maximum).\n"
            "  2. Highlight key insights from each relevant agent (market, clinical, patent, sourcing, etc.).\n"
            "  3. Provide actionable steps/recommendations focused on maximizing firm profitability (3-5 bullets).\n"
            "  4. Mention that a detailed report with all JSON responses and agent details has been generated.\n"
            "  5. Focus on business value and strategic recommendations.\n"
        )

        user_prompt = f"""
User query:
{user_query}

Planning details:
{json.dumps(plan, indent=2)}

Worker agent summaries:
{summaries_text}

Write a concise executive summary and actionable recommendations for the portfolio team.
"""

        final_answer = self.llm.chat(system_prompt, user_prompt)
        state["final_answer"] = final_answer
        return state

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self._plan_agents)
        workflow.add_node("run_workers", self._run_workers)
        workflow.add_node("generate_report", self._generate_report)
        workflow.add_node("final_answer", self._generate_final_answer)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        # Define edges
        workflow.add_edge("plan", "run_workers")
        workflow.add_edge("run_workers", "generate_report")
        workflow.add_edge("generate_report", "final_answer")
        workflow.add_edge("final_answer", END)
        
        return workflow.compile()

    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point - runs the full orchestration workflow.
        
        Returns:
            - user_query: Original query
            - plan: Planning decisions
            - worker_results: All agent responses
            - final_answer: Summary and recommendations
            - report: Report metadata with download link
        """
        initial_state: AgentState = {
            "user_query": user_query,
            "plan": {},
            "worker_results": [],
            "final_answer": "",
            "report": {}
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        return {
            "user_query": final_state["user_query"],
            "plan": final_state["plan"],
            "worker_results": final_state["worker_results"],
            "final_answer": final_state["final_answer"],
            "report": final_state["report"],
        }
