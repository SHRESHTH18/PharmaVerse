from fastapi import FastAPI, Query, Body,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from matplotlib import pyplot as plt


# In-memory storage for report data (in production, use a database)
report_storage: Dict[str, Dict[str, Any]] = {}

app = FastAPI()

# Allow your frontend / agent framework to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# a. IQVIA Insights Agent
# ============================================================================
@app.get("/api/iqvia")
def get_iqvia(molecule: str):
    """Queries IQVIA datasets for sales trends, volume shifts and therapy area dynamics"""
    if molecule.lower() == "metformin":
        return {
            "molecule": "Metformin",
            "markets": [
                {"country": "US", "sales_2024_musd": 800, "cagr_5y": 3.5},
                {"country": "India", "sales_2024_musd": 200, "cagr_5y": 7.2}
            ],
            "therapy_area": "Type 2 Diabetes",
            "unmet_need_flag": True,
            "competition_summary": {
                "top_competitors": ["Glucophage", "Fortamet", "Glumetza"],
                "market_concentration": "Highly competitive with multiple generics",
                "therapy_dynamics": "Stable growth driven by diabetes prevalence increase"
            }
        }
    elif molecule.lower() == "imatinib":
        return {
            "molecule": "Imatinib",
            "markets": [
                {"country": "US", "sales_2024_musd": 1200, "cagr_5y": -2.3},
                {"country": "EU", "sales_2024_musd": 650, "cagr_5y": -1.8},
                {"country": "India", "sales_2024_musd": 180, "cagr_5y": 4.5}
            ],
            "therapy_area": "Oncology - CML",
            "unmet_need_flag": False,
            "competition_summary": {
                "top_competitors": ["Dasatinib", "Nilotinib", "Bosutinib"],
                "market_concentration": "Moderate competition with newer TKIs",
                "therapy_dynamics": "Declining sales due to newer generation inhibitors"
            }
        }
    return {"molecule": molecule, "markets": [], "message": "No data available for this molecule"}


# ============================================================================
# b. EXIM Trends Agent
# ============================================================================
@app.get("/api/exim")
def get_exim_trends(
    product: str,
    country: Optional[str] = None,
    year: Optional[int] = 2024
):
    """Extracts export-import data for APIs/formulations across countries"""
    if product.lower() == "metformin api":
        return {
            "product": "Metformin API",
            "year": year,
            "trade_data": [
                {
                    "country": "India",
                    "exports_tonnes": 45000,
                    "imports_tonnes": 2000,
                    "net_position": "Net Exporter",
                    "top_destinations": ["US", "EU", "Brazil"],
                    "value_musd": 180
                },
                {
                    "country": "China",
                    "exports_tonnes": 62000,
                    "imports_tonnes": 500,
                    "net_position": "Net Exporter",
                    "top_destinations": ["US", "India", "EU"],
                    "value_musd": 248
                },
                {
                    "country": "US",
                    "exports_tonnes": 1200,
                    "imports_tonnes": 38000,
                    "net_position": "Net Importer",
                    "top_sources": ["China", "India"],
                    "value_musd": 152,
                    "import_dependency": "High (95%)"
                }
            ],
            "sourcing_insights": "Market dominated by Asian manufacturers, particularly China and India",
            "trend": "Increasing shift towards Indian suppliers due to geopolitical factors"
        }
    elif product.lower() == "paracetamol":
        return {
            "product": "Paracetamol",
            "year": year,
            "trade_data": [
                {
                    "country": "China",
                    "exports_tonnes": 85000,
                    "imports_tonnes": 100,
                    "net_position": "Net Exporter",
                    "top_destinations": ["US", "EU", "India", "Brazil"],
                    "value_musd": 340
                },
                {
                    "country": "India",
                    "exports_tonnes": 12000,
                    "imports_tonnes": 28000,
                    "net_position": "Net Importer",
                    "top_sources": ["China"],
                    "value_musd": 48,
                    "import_dependency": "Medium (70%)"
                }
            ],
            "sourcing_insights": "China dominates global paracetamol supply",
            "trend": "Growing concern over supply chain concentration"
        }
    return {"product": product, "message": "No trade data available"}


# ============================================================================
# c. Patent Landscape Agent
# ============================================================================
@app.get("/api/patents")
def get_patent_landscape(molecule: str, indication: Optional[str] = None):
    """Searches USPTO and other IP databases for active patents, expiry timelines and FTO flags"""
    if molecule.lower() == "imatinib":
        return {
            "molecule": "Imatinib",
            "indication": indication or "CML",
            "patent_status": [
                {
                    "patent_number": "US6521620B2",
                    "title": "Imatinib base and salts",
                    "holder": "Novartis AG",
                    "filing_date": "2000-04-07",
                    "expiry_date": "2015-05-01",
                    "status": "Expired",
                    "geography": "US"
                },
                {
                    "patent_number": "US7550590B2",
                    "title": "Crystal modification of imatinib mesylate",
                    "holder": "Novartis AG",
                    "filing_date": "2005-11-22",
                    "expiry_date": "2019-06-15",
                    "status": "Expired",
                    "geography": "US"
                }
            ],
            "fto_flag": "Clear - Primary patents expired",
            "competitive_landscape": {
                "total_active_patents": 0,
                "filing_trend": "Declining - molecule off-patent",
                "geographic_coverage": ["US", "EU", "Japan", "India"],
                "formulation_patents": 3,
                "combination_patents": 5
            },
            "generic_opportunity": "High - All major patents expired globally"
        }
    elif molecule.lower() == "semaglutide":
        return {
            "molecule": "Semaglutide",
            "indication": indication or "Type 2 Diabetes / Obesity",
            "patent_status": [
                {
                    "patent_number": "US8729019B2",
                    "title": "Protracted GLP-1 derivatives",
                    "holder": "Novo Nordisk",
                    "filing_date": "2011-03-18",
                    "expiry_date": "2031-03-18",
                    "status": "Active",
                    "geography": "US"
                },
                {
                    "patent_number": "US10751400B2",
                    "title": "Pharmaceutical formulation of semaglutide",
                    "holder": "Novo Nordisk",
                    "filing_date": "2017-06-15",
                    "expiry_date": "2037-06-15",
                    "status": "Active",
                    "geography": "US"
                }
            ],
            "fto_flag": "Blocked - Strong patent protection",
            "competitive_landscape": {
                "total_active_patents": 47,
                "filing_trend": "Very Active - ongoing R&D",
                "geographic_coverage": ["US", "EU", "Japan", "China", "India"],
                "formulation_patents": 12,
                "combination_patents": 8
            },
            "generic_opportunity": "Low - Not until 2031+ globally"
        }
    return {"molecule": molecule, "message": "No patent data available"}


# ============================================================================
# d. Clinical Trials Agent
# ============================================================================
@app.get("/api/clinical-trials")
def get_clinical_trials(
    molecule: Optional[str] = None,
    indication: Optional[str] = None,
    phase: Optional[str] = None
):
    """Fetches trial pipeline data from ClinicalTrials.gov or WHO ICTRP"""
    if molecule and molecule.lower() == "semaglutide":
        return {
            "molecule": "Semaglutide",
            "total_trials": 287,
            "active_trials": [
                {
                    "nct_id": "NCT04657497",
                    "title": "Semaglutide Effects on Heart Disease and Stroke in Obesity",
                    "sponsor": "Novo Nordisk",
                    "phase": "Phase 3",
                    "status": "Active, recruiting",
                    "enrollment": 17500,
                    "start_date": "2023-10-15",
                    "estimated_completion": "2028-12-31",
                    "indication": "Cardiovascular Disease / Obesity"
                },
                {
                    "nct_id": "NCT05051579",
                    "title": "Semaglutide in Alzheimer's Disease",
                    "sponsor": "University of Copenhagen",
                    "phase": "Phase 2",
                    "status": "Active, recruiting",
                    "enrollment": 200,
                    "start_date": "2024-03-01",
                    "estimated_completion": "2026-09-30",
                    "indication": "Alzheimer's Disease"
                },
                {
                    "nct_id": "NCT04657536",
                    "title": "Semaglutide for Fatty Liver Disease",
                    "sponsor": "Novo Nordisk",
                    "phase": "Phase 3",
                    "status": "Active, not recruiting",
                    "enrollment": 1200,
                    "start_date": "2022-08-10",
                    "estimated_completion": "2026-06-15",
                    "indication": "NASH/NAFLD"
                }
            ],
            "phase_distribution": {
                "Phase 1": 23,
                "Phase 2": 89,
                "Phase 3": 67,
                "Phase 4": 108
            },
            "sponsor_profiles": {
                "Novo Nordisk": 142,
                "Academic Institutions": 98,
                "Other Pharma": 47
            },
            "geographic_distribution": {
                "US": 156,
                "EU": 87,
                "Asia": 44
            }
        }
    elif indication and indication.lower() == "obesity":
        return {
            "indication": "Obesity",
            "total_trials": 1543,
            "active_trials": [
                {
                    "nct_id": "NCT04657497",
                    "title": "Semaglutide Effects on Heart Disease and Stroke in Obesity",
                    "sponsor": "Novo Nordisk",
                    "phase": "Phase 3",
                    "molecule": "Semaglutide",
                    "status": "Active, recruiting"
                },
                {
                    "nct_id": "NCT05296603",
                    "title": "Tirzepatide for Weight Management in Obesity",
                    "sponsor": "Eli Lilly",
                    "phase": "Phase 3",
                    "molecule": "Tirzepatide",
                    "status": "Active, recruiting"
                }
            ],
            "phase_distribution": {
                "Phase 1": 234,
                "Phase 2": 567,
                "Phase 3": 398,
                "Phase 4": 344
            },
            "top_molecules": ["Semaglutide", "Tirzepatide", "Liraglutide", "Orlistat"]
        }
    return {"message": "Specify molecule or indication parameter"}


# ============================================================================
# e. Internal Knowledge Agent
# ============================================================================
@app.get("/api/internal-knowledge")
def get_internal_knowledge(
    document_type: Optional[str] = None,
    topic: Optional[str] = None,
    search_query: Optional[str] = None
):
    """Retrieves and summarizes internal documents (MINS, strategy decks, field insights)"""
    if topic and topic.lower() == "diabetes strategy":
        return {
            "topic": "Diabetes Strategy",
            "documents_found": 8,
            "key_takeaways": [
                "Focus on GLP-1 receptor agonists as primary growth driver for 2025-2027",
                "India and Brazil identified as key emerging markets for diabetes portfolio",
                "Digital health integration planned for Q2 2026",
                "Partnership discussions ongoing with 3 major insulin manufacturers"
            ],
            "documents": [
                {
                    "title": "Diabetes Portfolio Strategy 2025-2030",
                    "type": "Strategy Deck",
                    "date": "2024-11-15",
                    "author": "Strategic Planning Team",
                    "summary": "Comprehensive strategy outlining market positioning, competitive landscape, and growth initiatives for diabetes franchise",
                    "download_link": "/docs/diabetes_strategy_2025.pdf"
                },
                {
                    "title": "Field Insights - Diabetes Market Q3 2024",
                    "type": "Field Report",
                    "date": "2024-10-05",
                    "author": "Sales & Marketing",
                    "summary": "Physician feedback on current diabetes treatments, unmet needs, and competitor activities",
                    "download_link": "/docs/field_insights_diabetes_q3.pdf"
                },
                {
                    "title": "MINS - Diabetes Franchise Review",
                    "type": "Meeting Minutes",
                    "date": "2024-09-20",
                    "author": "Executive Committee",
                    "summary": "Strategic review of diabetes portfolio performance and future investment priorities",
                    "download_link": "/docs/mins_diabetes_sept2024.pdf"
                }
            ],
            "comparative_analysis": {
                "our_market_share": "12.3%",
                "top_competitor_share": "28.7%",
                "growth_rate_vs_market": "+2.1% above market average"
            }
        }
    elif document_type and document_type.lower() == "mins":
        return {
            "document_type": "Meeting Minutes",
            "recent_documents": [
                {
                    "title": "MINS - Executive Committee Meeting",
                    "date": "2024-12-01",
                    "topics": ["Q4 Performance", "2025 Budget", "Pipeline Review"],
                    "summary": "Approved 2025 budget with 15% increase in R&D spend focusing on oncology and rare diseases",
                    "download_link": "/docs/mins_exec_dec2024.pdf"
                },
                {
                    "title": "MINS - R&D Portfolio Review",
                    "date": "2024-11-28",
                    "topics": ["Phase 3 Readouts", "Early Pipeline", "Partnership Opportunities"],
                    "summary": "Positive Phase 3 data for Asset XYZ; greenlight for 3 new Phase 1 studies",
                    "download_link": "/docs/mins_rd_nov2024.pdf"
                }
            ]
        }
    return {
        "message": "Specify document_type, topic, or search_query parameter",
        "available_types": ["MINS", "Strategy Deck", "Field Report", "Market Analysis"]
    }


# ============================================================================
# f. Web Intelligence Agent
# ============================================================================
@app.get("/api/web-intelligence")
def get_web_intelligence(
    query: str,
    source_type: Optional[str] = None
):
    """Performs real-time web search for guidelines, scientific publications, news and patient forums"""
    if "diabetes guidelines" in query.lower():
        return {
            "query": query,
            "results_count": 127,
            "top_results": [
                {
                    "title": "ADA Standards of Care in Diabetes - 2025",
                    "source": "American Diabetes Association",
                    "url": "https://diabetesjournals.org/care/issue/48/Supplement_1",
                    "date": "2025-01-01",
                    "type": "Clinical Guideline",
                    "summary": "Updated recommendations for diabetes management including new GLP-1 RA guidance for cardiovascular risk reduction",
                    "key_quotes": [
                        "GLP-1 receptor agonists are now recommended as first-line therapy for patients with T2D and established cardiovascular disease",
                        "Metformin remains cost-effective first-line option for most patients without CVD"
                    ],
                    "credibility_score": "High - Official ADA guideline"
                },
                {
                    "title": "EASD/ADA Consensus Report on Type 2 Diabetes Management",
                    "source": "European Association for the Study of Diabetes",
                    "url": "https://easd.org/consensus-2024",
                    "date": "2024-10-15",
                    "type": "Clinical Guideline",
                    "summary": "Joint consensus emphasizing individualized treatment approaches and SGLT2i/GLP-1 RA benefits",
                    "key_quotes": [
                        "Treatment decisions should be based on patient-centered factors including comorbidities, cost, and preferences"
                    ],
                    "credibility_score": "High - Joint EASD/ADA consensus"
                }
            ],
            "scientific_publications": [
                {
                    "title": "Cardiovascular Outcomes with Semaglutide in Obesity",
                    "journal": "New England Journal of Medicine",
                    "doi": "10.1056/NEJMoa2307563",
                    "date": "2024-08-15",
                    "summary": "SELECT trial demonstrated 20% reduction in major adverse cardiovascular events"
                }
            ],
            "news_articles": [
                {
                    "title": "FDA Approves New Diabetes-Obesity Dual Indication",
                    "source": "FiercePharma",
                    "date": "2024-12-05",
                    "url": "https://fiercepharma.com/...",
                    "summary": "Regulatory approval expands treatment options for patients with both conditions"
                }
            ]
        }
    elif "metformin" in query.lower() and "patient" in query.lower():
        return {
            "query": query,
            "results_count": 2340,
            "patient_forum_insights": [
                {
                    "source": "DiabetesForum.com",
                    "thread_title": "Metformin side effects - your experience?",
                    "date": "2024-11-30",
                    "post_count": 187,
                    "key_themes": ["GI side effects", "Extended release formulation", "Taking with food"],
                    "sentiment": "Mixed - effective but GI issues common",
                    "sample_quotes": [
                        "Switched to extended release and side effects much better",
                        "Been on it 5 years, no issues if I take with meals"
                    ]
                },
                {
                    "source": "Reddit r/diabetes",
                    "thread_title": "Metformin vs newer diabetes meds",
                    "date": "2024-12-02",
                    "post_count": 94,
                    "key_themes": ["Cost comparison", "Efficacy", "Weight loss"],
                    "sentiment": "Positive - valued for cost-effectiveness",
                    "sample_quotes": [
                        "Metformin is cheap and works. Newer drugs better for weight loss but $$",
                        "Insurance won't cover GLP-1s so sticking with metformin"
                    ]
                }
            ],
            "credible_sources_count": 45,
            "peer_reviewed_articles": 892
        }
    return {
        "query": query,
        "message": "Search results would appear here",
        "source_types_available": ["guidelines", "publications", "news", "patient_forums"]
    }

# import uuid
# import os
# import io
# from pathlib import Path
# from datetime import datetime
# from typing import Dict, Any

from fastapi import Query, Body
from fastapi.responses import FileResponse
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt

# ============================================================================
# Storage
# ============================================================================
REPORT_DIR = Path("reports/generated")
CHART_DIR = REPORT_DIR / "charts"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Chart Generator
# ============================================================================
# def generate_chart(chart: Dict[str, Any], path: Path):
#     labels = chart["data"]["labels"]
#     values = chart["data"]["values"]

#     if not labels or not values:
#         return None

#     plt.figure(figsize=(6, 4))

#     ctype = chart["recommended_chart"]
#     if ctype == "bar":
#         plt.bar(labels, values)
#     elif ctype == "line":
#         plt.plot(labels, values, marker="o")
#     elif ctype == "pie":
#         plt.pie(values, labels=labels, autopct="%1.1f%%")

#     plt.title(chart["title"])
#     plt.tight_layout()
#     plt.savefig(path)
#     plt.close()
#     return path
def generate_chart(chart: Dict[str, Any], path: Path):
    labels = chart["data"].get("labels", [])
    values = chart["data"].get("values", [])

    # ✅ HARD VALIDATION
    numeric_values = []
    for v in values:
        try:
            numeric_values.append(float(v))
        except (ValueError, TypeError):
            # ❌ Skip charts with invalid numeric data
            return None

    if not labels or not numeric_values:
        return None

    plt.figure(figsize=(6, 4))

    ctype = chart.get("recommended_chart")

    if ctype == "bar":
        plt.bar(labels, numeric_values)
    elif ctype == "line":
        plt.plot(labels, numeric_values, marker="o")
    elif ctype == "pie":
        # pie cannot have negatives
        if any(v < 0 for v in numeric_values):
            return None
        plt.pie(numeric_values, labels=labels, autopct="%1.1f%%")
    else:
        return None

    plt.title(chart.get("title", ""))
    plt.tight_layout()
    plt.savefig(str(path))
    plt.close()
    return path

# ============================================================================
# PDF Generator
# ============================================================================
# def generate_pdf(report_id: str, report_data: Dict[str, Any], output_path: Path):
#     styles = getSampleStyleSheet()
#     styles.add(ParagraphStyle(
#         name="AgentHeader",
#         fontSize=18,
#         spaceAfter=12,
#         textColor=colors.HexColor("#2c3e50")
#     ))

#     doc = SimpleDocTemplate(
#         output_path,
#         pagesize=A4,
#         leftMargin=40,
#         rightMargin=40,
#         topMargin=40,
#         bottomMargin=40,
#     )

#     story = []

#     # Cover
#     story.append(Paragraph("PharmaVerse Innovation Assessment", styles["Title"]))
#     story.append(Spacer(1, 0.3 * inch))
#     story.append(Paragraph(report_data["topic"], styles["Heading2"]))
#     story.append(Spacer(1, 0.2 * inch))
#     story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
#     story.append(PageBreak())

#     # Executive Summary
#     story.append(Paragraph("Executive Summary", styles["Heading1"]))
#     story.append(Paragraph(report_data.get("final_answer", ""), styles["Normal"]))
#     story.append(PageBreak())

#     demographics = report_data.get("demographics", {}).get("agents", {})

#     # Agent Sections
#     for agent in report_data["worker_results"]:
#         agent_name = agent["agent"]
#         story.append(Paragraph(agent_name, styles["AgentHeader"]))
#         story.append(Paragraph(agent["summary"], styles["Normal"]))
#         story.append(Spacer(1, 0.2 * inch))

#         for chart in demographics.get(agent_name, []):
#             img_path = CHART_DIR / f"{report_id}_{chart['id']}.png"
#             saved = generate_chart(chart, img_path)
#             if saved:
#                 story.append(Paragraph(chart["title"], styles["Heading3"]))
#                 story.append(Paragraph(chart["insight"], styles["Italic"]))
#                 story.append(Image(saved, width=5 * inch, height=3 * inch))
#                 story.append(Spacer(1, 0.3 * inch))

#         story.append(PageBreak())

#     doc.build(story)
def generate_pdf(report_id: str, report_data: Dict[str, Any], output_path: Path):
    """
    Generate a professional-looking PDF report with:
      - Cover page
      - Executive summary
      - Per-agent sections (only if demographics / charts available)
      - Charts appended after each agent summary

    NOTE: To keep this endpoint self-contained and robust in offline
    environments, we format agent summaries heuristically instead of
    calling an LLM again here. The summaries coming from agents are
    already LLM-generated.
    """
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="AgentHeader",
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor("#2c3e50")
    ))
    styles.add(ParagraphStyle(
        name="AgentSummary",
        fontSize=11,
        leading=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor("#1f2933")
    ))

    # Convert Path → str for reportlab
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story: List[Any] = []

    topic = report_data.get("topic", "Innovation Opportunity Assessment")
    final_answer = report_data.get("final_answer", "")

    # ------------------------------------------------------------------
    # Cover
    # ------------------------------------------------------------------
    story.append(Paragraph("PharmaVerse Innovation Assessment", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(topic, styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )
    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Executive Summary (already LLM-generated)
    # ------------------------------------------------------------------
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    if final_answer:
        # final_answer may contain markdown-like formatting; keep simple
        for line in final_answer.split("\n\n"):
            if not line.strip():
                continue
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))
    else:
        story.append(Paragraph("No executive summary available.", styles["Normal"]))
    story.append(PageBreak())

    # ------------------------------------------------------------------
    # Agent Sections with demographics (if available)
    # Use demographics exactly as passed from the 8080 API:
    #  - Either {"agents": {...}}  (direct)
    #  - Or {"agent": "...", "raw": {"agents": {...}}}  (via DemographicAgent)
    # ------------------------------------------------------------------
    raw_demographics = report_data.get("demographics") or {}
    if isinstance(raw_demographics, dict) and "agents" in raw_demographics:
        demographics = raw_demographics.get("agents") or {}
    elif isinstance(raw_demographics, dict) and isinstance(raw_demographics.get("raw"), dict):
        demographics = raw_demographics["raw"].get("agents") or {}
    else:
        demographics = {}
    worker_results = report_data.get("worker_results") or []

    # Color palette per agent for demographic visuals
    agent_colors = {
        "IQVIA Insights Agent": "#7c3aed",      # purple
        "EXIM Trends Agent": " #2563eb",        # blue
        "Patent Landscape Agent": "#16a34a",    # green
        "Clinical Trials Agent": "#dc2626",     # red
        "Internal Knowledge Agent": "#4f46e5",  # indigo
        "Web Intelligence Agent": "#0891b2",    # cyan
    }

    for agent in worker_results:
        agent_name = agent.get("agent", "Unknown Agent")
        agent_summary = agent.get("summary", "").strip()
        agent_charts = demographics.get(agent_name) or []

        # ------------------------------------------------------------------
        # Agent header
        # ------------------------------------------------------------------
        story.append(Paragraph(agent_name, styles["AgentHeader"]))

        # Lightly structure the agent summary (already LLM-generated text)
        if agent_summary:
            story.append(Paragraph("Narrative Summary", styles["SectionTitle"]))
            for block in agent_summary.split("\n\n"):
                text = block.strip()
                if not text:
                    continue
                story.append(Paragraph(text, styles["AgentSummary"]))
                story.append(Spacer(1, 0.05 * inch))
            story.append(Spacer(1, 0.2 * inch))

        # ------------------------------------------------------------------
        # Charts / Visual Insights (optional)
        # ------------------------------------------------------------------
        chart_images: List[Path] = []
        if agent_charts:
            story.append(Paragraph("Visual Insights", styles["SectionTitle"]))

            for chart in agent_charts:
                try:
                    img_path = CHART_DIR / f"{report_id}_{chart.get('id', chart.get('title', 'chart'))}.png"
                    saved = generate_chart(chart, img_path)
                    if not saved:
                        continue
                    chart_images.append(saved)

                    title = chart.get("title", "Chart")
                    insight = chart.get("insight", "")
                    color = agent_colors.get(agent_name, "#111827")

                    # Colored title and insight per agent
                    story.append(Paragraph(f'<font color="{color}">{title}</font>', styles["Heading3"]))
                    if insight:
                        story.append(Paragraph(f'<font color="{color}">{insight}</font>', styles["Italic"]))
                    story.append(Image(str(saved), width=5 * inch, height=3 * inch))
                    story.append(Spacer(1, 0.3 * inch))
                except Exception as e:
                    # Skip problematic charts but don't break the whole report
                    print(f"[REPORT][{agent_name}] Chart generation failed: {e}")
                    continue

        # Add reasonable spacing after each agent section instead of page break
        story.append(Spacer(1, 0.5 * inch))

    doc.build(story)
    print(f"[REPORT GENERATED] {output_path.resolve()}")

# ============================================================================
# API: Generate Report
# ============================================================================
    # @app.post("/api/generate-report")
    # def generate_report(report_data: Dict[str, Any] = Body(...)):
    #     report_id = f"RPT_{uuid.uuid4().hex[:8]}"
    #     pdf_path = REPORT_DIR / f"{report_id}.pdf"

    #     generate_pdf(report_id, report_data, pdf_path)

    #     return {
    #         "report_id": report_id,
    #         "status": "Generated",
    #         "download_link": f"/downloads/reports/{report_id}.pdf"
    #     }
# @app.post("/api/generate-report")
# async def generate_report(request: Request):
#     """Generate a comprehensive PDF report"""
#     try:
#         data = await request.json()
        
#         topic = data.get("topic", "Report")
#         user_query = data.get("user_query", "")
#         plan = data.get("plan", {})
#         worker_results = data.get("worker_results", [])
#         demographics = data.get("demographics", {})
#         include_sections = data.get("include_sections", [])
        
#         # Generate report ID
#         report_id = f"report_{int(datetime.now().timestamp())}"
        
#         # Store report data
#         report_storage[report_id] = {
#             "topic": topic,
#             "user_query": user_query,
#             "plan": plan,
#             "worker_results": worker_results,
#             "demographics": demographics,
#             "include_sections": include_sections,
#             "timestamp": datetime.now().isoformat()
#         }
        
#         return {
#             "status": "success",
#             "report_id": report_id,
#             "download_url": f"/downloads/reports/{report_id}.pdf",
#             "message": f"Report '{topic}' generated successfully"
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }
@app.post("/api/generate-report")
async def generate_report(request: Request):
    """Generate a comprehensive PDF report"""
    try:
        data = await request.json()

        topic = data.get("topic", "Report")
        user_query = data.get("user_query", "")
        plan = data.get("plan", {})
        worker_results = data.get("worker_results", [])
        demographics = data.get("demographics", {})
        final_answer = data.get("final_answer", "")
        include_sections = data.get("include_sections", [])

        # ✅ Generate report ID
        report_id = f"report_{int(datetime.now().timestamp())}"

        # ✅ Define real PDF path
        pdf_path = REPORT_DIR / f"{report_id}.pdf"

        # ✅ BUILD REPORT DATA
        report_data = {
            "topic": topic,
            "user_query": user_query,
            "plan": plan,
            "worker_results": worker_results,
            "demographics": demographics,
            "final_answer": final_answer,
            "include_sections": include_sections,
        }

        # 🔥 THIS WAS MISSING — ACTUALLY CREATE THE PDF
        generate_pdf(
            report_id=report_id,
            report_data=report_data,
            output_path=pdf_path
        )

        # ✅ Store metadata (optional, but fine)
        report_storage[report_id] = {
            "path": str(pdf_path),
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "report_id": report_id,
            "download_url": f"/downloads/reports/{report_id}.pdf",
            "message": f"Report '{topic}' generated successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ============================================================================
# API: Download Report
# ============================================================================
# @app.get("/downloads/reports/{report_id}.pdf")
# def download_report(report_id: str):
#     path = REPORT_DIR / f"{report_id}.pdf"
#     if not path.exists():
#         return {"error": "Report not found"}

#     return FileResponse(
#         path,
#         media_type="application/pdf",
#         filename=f"{report_id}.pdf"
#     )
@app.get("/downloads/reports/{report_id}.pdf")
def download_report(report_id: str):
    path = REPORT_DIR / f"{report_id}.pdf"

    if not path.exists():
        return {
            "status": "processing",
            "message": "Report is still being generated. Please try again in a few seconds."
        }

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=f"{report_id}.pdf"
    )

# ============================================================================
# Utility endpoint to get all available endpoints
# ============================================================================
@app.get("/")
def root():
    return {
        "message": "PharmaVerse Mock API",
        "version": "1.0.0",
        "endpoints": {
            "iqvia": "/api/iqvia?molecule={molecule_name}",
            "exim": "/api/exim?product={product_name}&country={country}&year={year}",
            "patents": "/api/patents?molecule={molecule_name}&indication={indication}",
            "clinical_trials": "/api/clinical-trials?molecule={molecule}&indication={indication}&phase={phase}",
            "internal_knowledge": "/api/internal-knowledge?document_type={type}&topic={topic}",
            "web_intelligence": "/api/web-intelligence?query={search_query}&source_type={type}",
            "generate_report": "/api/generate-report?report_type={pdf|excel}&topic={topic}"
        },
        "documentation": "/docs"
    }