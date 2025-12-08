from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

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


# ============================================================================
# g. Report Generator Agent
# ============================================================================
@app.post("/api/generate-report")
def generate_report(
    report_type: str = Query(..., description="pdf or excel"),
    topic: str = Query(..., description="Report topic/title"),
    include_sections: Optional[List[str]] = Query(None, description="Sections to include")
):
    """Formats the synthesized response into a polished PDF or Excel report"""
    report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if report_type.lower() == "pdf":
        return {
            "report_id": report_id,
            "report_type": "PDF",
            "topic": topic,
            "status": "Generated",
            "generated_at": datetime.now().isoformat(),
            "sections_included": include_sections or [
                "Executive Summary",
                "Market Analysis",
                "Competitive Landscape",
                "Clinical Pipeline",
                "Patent Status",
                "Recommendations"
            ],
            "page_count": 24,
            "file_size_mb": 3.2,
            "download_link": f"/downloads/reports/{report_id}.pdf",
            "preview_url": f"/preview/reports/{report_id}",
            "charts_included": [
                "Market Size Trend Chart",
                "CAGR Comparison Bar Chart",
                "Phase Distribution Pie Chart",
                "Patent Expiry Timeline"
            ],
            "tables_included": [
                "Market Size by Geography",
                "Top 10 Competitors",
                "Active Clinical Trials",
                "Patent Status Summary"
            ]
        }
    elif report_type.lower() == "excel":
        return {
            "report_id": report_id,
            "report_type": "Excel",
            "topic": topic,
            "status": "Generated",
            "generated_at": datetime.now().isoformat(),
            "worksheets": [
                {
                    "name": "Summary Dashboard",
                    "type": "Charts & KPIs",
                    "description": "Executive summary with key metrics and visualizations"
                },
                {
                    "name": "Market Data",
                    "type": "Data Table",
                    "rows": 156,
                    "description": "Detailed market size, sales, and CAGR data by geography"
                },
                {
                    "name": "Clinical Trials",
                    "type": "Data Table",
                    "rows": 47,
                    "description": "Active trials with phase, sponsor, and timeline information"
                },
                {
                    "name": "Patent Landscape",
                    "type": "Data Table",
                    "rows": 23,
                    "description": "Patent status, expiry dates, and FTO analysis"
                },
                {
                    "name": "EXIM Data",
                    "type": "Data Table",
                    "rows": 89,
                    "description": "Import/export volumes and trade flow analysis"
                }
            ],
            "file_size_mb": 1.8,
            "download_link": f"/downloads/reports/{report_id}.xlsx",
            "features": [
                "Pivot tables enabled",
                "Interactive charts",
                "Data validation",
                "Conditional formatting"
            ]
        }
    return {
        "error": "Invalid report_type. Choose 'pdf' or 'excel'"
    }


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