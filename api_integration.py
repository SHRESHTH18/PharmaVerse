# api_integration.py
# Backend API endpoints to integrate with the frontend website
import os
import sys
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from dotenv import load_dotenv

# Redis is optional - only import if available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Add pharma_agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pharma_agents'))
from pharma_agents.master_agent import MasterAgent
from pharma_agents.config import settings

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="PharmaVerse API Integration")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = {}
active_websockets: Dict[str, List[WebSocket]] = {}

# Import report_storage from mock_api if available
try:
    from mock_api import report_storage
except ImportError:
    report_storage: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# Pydantic Models
# ============================================================================

class OrchestrateRequest(BaseModel):
    molecule_name: str
    indication: str
    geography: Optional[str] = "Global"
    timeframe: Optional[str] = "2024-2026"
    strategic_question: Optional[str] = ""

class ChatRequest(BaseModel):
    session_id: str
    message: str

# ============================================================================
# Helper Functions
# ============================================================================

def get_session(session_id: str) -> Dict[str, Any]:
    """Get session data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

def store_session(session_id: str, data: Dict[str, Any]):
    """Store session data"""
    sessions[session_id] = {
        **data,
        "updated_at": datetime.now().isoformat()
    }

async def broadcast_to_session(session_id: str, message: Dict[str, Any]):
    """Broadcast message to all WebSocket connections for a session"""
    if session_id in active_websockets:
        disconnected = []
        for ws in active_websockets[session_id]:
            try:
                await ws.send_json(message)
            except:
                disconnected.append(ws)
        
        # Remove disconnected websockets
        for ws in disconnected:
            active_websockets[session_id].remove(ws)

# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/api/orchestrate")
async def orchestrate(request: OrchestrateRequest):
    """Handle 'Launch Agent Run' from Case Setup Screen"""
    session_id = str(uuid.uuid4())
    
    # Build user query from form data
    user_query = (
        f"Evaluate the innovation opportunity for {request.molecule_name} in {request.indication}. "
        f"Geography: {request.geography}. "
        f"Timeframe: {request.timeframe}. "
        f"Strategic Question: {request.strategic_question}"
    )
    
    # Initialize session
    session_data = {
        "session_id": session_id,
        "molecule": {
            "name": request.molecule_name,
            "indication": request.indication,
            "geography": request.geography,
            "timeframe": request.timeframe,
            "strategic_question": request.strategic_question
        },
        "user_query": user_query,
        "status": "processing",
        "agent_results": {},
        "chat_history": [],
        "created_at": datetime.now().isoformat()
    }
    store_session(session_id, session_data)
    
    # Run agents asynchronously
    asyncio.create_task(run_agents_async(session_id, user_query))
    
    return {
        "session_id": session_id,
        "status": "processing",
        "agents_launched": ["iqvia", "exim", "patents", "trials", "internal", "web"]
    }

@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status for polling"""
    if session_id not in sessions:
        return {"status": "not_found"}
    session = sessions[session_id]
    return {
        "status": session.get("status", "processing"),
        "agent_results": list(session.get("agent_results", {}).keys()),
        "progress": len(session.get("agent_results", {})) / 6 * 100
    }

async def run_agents_async(session_id: str, user_query: str):
    """Run agents asynchronously and emit updates"""
    try:
        # Small delay to ensure session is stored
        await asyncio.sleep(0.1)
        master = MasterAgent()
        
        # Send initial message
        await broadcast_to_session(session_id, {
            "type": "chat_message",
            "sender": "master",
            "message": f"Starting comprehensive analysis. I'm coordinating with all worker agents..."
        })
        
        # Run the master agent workflow
        initial_state = {
            "user_query": user_query,
            "plan": {},
            "worker_results": [],
            "final_answer": "",
            "report": {}
        }
        
        # Simulate step-by-step execution to emit status updates
        # Step 1: Plan
        await broadcast_to_session(session_id, {
            "type": "agent_status",
            "agent": "master",
            "status": "running",
            "message": "Planning which agents to call..."
        })
        
        # Create temporary state for planning
        temp_state = {
            "user_query": user_query,
            "plan": {},
            "worker_results": [],
            "final_answer": "",
            "report": {}
        }
        plan_state = master._plan_agents(temp_state)
        plan = plan_state["plan"]
        session = get_session(session_id)
        session["plan"] = plan
        store_session(session_id, session)
        
        # Step 2: Run workers
        worker_results = []
        agent_order = [
            ("iqvia", "IQVIA Insights Agent", "🔍 Analyzing market data..."),
            ("exim", "EXIM Trends Agent", "🌍 Analyzing trade data..."),
            ("patents", "Patent Landscape Agent", "⚖️ Searching IP databases..."),
            ("trials", "Clinical Trials Agent", "🔬 Querying ClinicalTrials.gov..."),
            ("internal", "Internal Knowledge Agent", "📊 Searching internal documents..."),
            ("web", "Web Intelligence Agent", "🌐 Searching for guidelines and publications...")
        ]
        
        plan_map = {
            "iqvia": plan.get("call_iqvia", True),
            "exim": plan.get("call_exim", True),
            "patents": plan.get("call_patents", True),
            "trials": plan.get("call_clinical", True),
            "internal": plan.get("call_internal", True),
            "web": plan.get("call_webintel", True)
        }
        
        context = user_query
        if plan.get("molecule"):
            context += f"\nPrimary molecule: {plan['molecule']}"
        if plan.get("indication"):
            context += f"\nPrimary indication: {plan['indication']}"
        
        for agent_key, agent_display, message in agent_order:
            if not plan_map.get(agent_key, True):
                continue
                
            await broadcast_to_session(session_id, {
                "type": "agent_status",
                "agent": agent_key,
                "status": "running",
                "message": message
            })
            
            await broadcast_to_session(session_id, {
                "type": "chat_message",
                "sender": "master",
                "message": message
            })
            
            try:
                # Run the appropriate agent
                if agent_key == "iqvia":
                    result = master.iqvia_agent.run(context)
                elif agent_key == "exim":
                    exim_query = context
                    if plan.get("molecule"):
                        exim_query += f"\nProduct: {plan['molecule']} API"
                    result = master.exim_agent.run(exim_query)
                elif agent_key == "patents":
                    result = master.patent_agent.run(context)
                elif agent_key == "trials":
                    result = master.ct_agent.run(context)
                elif agent_key == "internal":
                    result = master.internal_agent.run(context)
                elif agent_key == "web":
                    result = master.web_agent.run(context)
                else:
                    continue
                
                worker_results.append(result)
                
                # Update session
                session = get_session(session_id)
                session["agent_results"][agent_key] = result
                store_session(session_id, session)
                
                # Send completion update
                await broadcast_to_session(session_id, {
                    "type": "agent_status",
                    "agent": agent_key,
                    "status": "done"
                })
                
                # Send agent result with chat message
                summary_text = result.get('summary', 'Analysis complete.')
                summary_preview = summary_text[:150] + "..." if len(summary_text) > 150 else summary_text
                
                await broadcast_to_session(session_id, {
                    "type": "chat_message",
                    "sender": agent_key,
                    "message": summary_preview
                })
                
                await broadcast_to_session(session_id, {
                    "type": "agent_result",
                    "agent": agent_key,
                    "data": result.get("raw", {}),
                    "summary": result.get("summary", ""),
                    "message": f"{agent_display} completed"
                })
                
                # Small delay for smooth UI updates
                await asyncio.sleep(0.5)
                
            except Exception as e:
                await broadcast_to_session(session_id, {
                    "type": "agent_status",
                    "agent": agent_key,
                    "status": "error",
                    "message": f"Error: {str(e)}"
                })
        
        # Step 3: Generate final answer
        final_answer_state = master._generate_final_answer({
            "user_query": user_query,
            "plan": plan,
            "worker_results": worker_results,
            "final_answer": "",
            "report": {}
        })
        
        # Update session with final answer
        session = get_session(session_id)
        session["final_answer"] = final_answer_state["final_answer"]
        session["worker_results"] = worker_results
        session["status"] = "completed"
        store_session(session_id, session)
        
        # Send final message
        await broadcast_to_session(session_id, {
            "type": "chat_message",
            "sender": "master",
            "message": "Analysis complete! I've gathered insights from all agents. You can explore the results in the tabs on the right, or ask me specific questions."
        })
        
    except Exception as e:
        await broadcast_to_session(session_id, {
            "type": "chat_message",
            "sender": "master",
            "message": f"⚠️ An error occurred during analysis: {str(e)}"
        })
        session = get_session(session_id)
        session["status"] = "error"
        store_session(session_id, session)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    # Add to active connections
    if session_id not in active_websockets:
        active_websockets[session_id] = []
    active_websockets[session_id].append(websocket)
    
    try:
        # Send initial session data if available
        if session_id in sessions:
            session = sessions[session_id]
            await websocket.send_json({
                "type": "session_data",
                "data": session
            })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Echo or process any incoming messages
                await websocket.send_json({"type": "pong", "message": "Connection active"})
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Remove from active connections
        if session_id in active_websockets:
            if websocket in active_websockets[session_id]:
                active_websockets[session_id].remove(websocket)

# @app.post("/api/chat")
# async def chat(request: ChatRequest):
#     """Handle chat messages from user"""
#     session = get_session(request.session_id)
    
#     # Add user message to chat history
#     session["chat_history"].append({
#         "sender": "user",
#         "message": request.message,
#         "timestamp": datetime.now().isoformat()
#     })
    
#     # Initialize master agent
#     master = MasterAgent()
    
#     # Simple keyword-based routing (can be enhanced with LLM)
#     lower_message = request.message.lower()
    
#     agent_to_trigger = None
#     response_message = ""
    
#     if "market" in lower_message or "sales" in lower_message or "iqvia" in lower_message:
#         agent_to_trigger = "iqvia"
#         response_message = "Let me pull the latest market data for you..."
#     elif "patent" in lower_message or "ip" in lower_message or "fto" in lower_message:
#         agent_to_trigger = "patents"
#         response_message = "Checking the patent landscape..."
#     elif "trial" in lower_message or "clinical" in lower_message:
#         agent_to_trigger = "trials"
#         response_message = "Searching clinical trials databases..."
#     elif "trade" in lower_message or "export" in lower_message or "import" in lower_message or "exim" in lower_message:
#         agent_to_trigger = "exim"
#         response_message = "Analyzing trade data..."
#     elif "internal" in lower_message or "strategy" in lower_message:
#         agent_to_trigger = "internal"
#         response_message = "Searching internal knowledge base..."
#     elif "guideline" in lower_message or "publication" in lower_message or "web" in lower_message:
#         agent_to_trigger = "web"
#         response_message = "Searching web intelligence sources..."
#     else:
#         response_message = f"I understand you're asking about: \"{request.message}\". Let me gather relevant information from our agents. You can also explore the tabs on the right for detailed insights."
    
#     # If agent needs to be triggered and hasn't run yet
#     if agent_to_trigger and agent_to_trigger not in session.get("agent_results", {}):
#         molecule = session["molecule"]["name"]
#         context = session["user_query"]
        
#         try:
#             if agent_to_trigger == "iqvia":
#                 result = master.iqvia_agent.run(context)
#             elif agent_to_trigger == "exim":
#                 result = master.exim_agent.run(context)
#             elif agent_to_trigger == "patents":
#                 result = master.patent_agent.run(context)
#             elif agent_to_trigger == "trials":
#                 result = master.ct_agent.run(context)
#             elif agent_to_trigger == "internal":
#                 result = master.internal_agent.run(context)
#             elif agent_to_trigger == "web":
#                 result = master.web_agent.run(context)
            
#             session["agent_results"][agent_to_trigger] = result
#             store_session(request.session_id, session)
            
#         except Exception as e:
#             response_message = f"Sorry, I encountered an error: {str(e)}"
    
#     # Add response to chat history
#     session["chat_history"].append({
#         "sender": "master",
#         "message": response_message,
#         "timestamp": datetime.now().isoformat()
#     })
#     store_session(request.session_id, session)
    
#     return {
#         "response": response_message,
#         "sender": "master",
#         "agents_triggered": [agent_to_trigger] if agent_to_trigger else []
#     }
# @app.post("/api/chat")
# async def chat(request: ChatRequest):
#     """Handle chat follow-up questions using existing agent data"""
#     session = get_session(request.session_id)

#     # Store user message
#     session["chat_history"].append({
#         "sender": "user",
#         "message": request.message,
#         "timestamp": datetime.now().isoformat()
#     })

#     lower_message = request.message.lower()
#     agent_results = session.get("agent_results", {})

#     # ---- Intent detection ----
#     intent_map = {
#         "iqvia": ["market", "sales", "cagr", "revenue"],
#         "patents": ["patent", "ip", "fto", "exclusivity"],
#         "trials": ["trial", "clinical", "phase"],
#         "exim": ["trade", "export", "import"],
#         "internal": ["internal", "strategy"],
#         "web": ["guideline", "publication", "news", "web"],
#     }

#     selected_agent = None
#     for agent, keywords in intent_map.items():
#         if any(k in lower_message for k in keywords):
#             selected_agent = agent
#             break

#     # ---- Build response ----
#     if not selected_agent:
#         response_message = (
#             "This question goes beyond the data collected so far. "
#             "Please run a new analysis if you’d like deeper insights."
#         )

#     elif selected_agent not in agent_results:
#         response_message = (
#             "That information was not generated in the current analysis. "
#             "Please run a fresh analysis to explore this area."
#         )

#     else:
#         # ✅ Use existing agent result
#         result = agent_results[selected_agent]
#         summary = result.get("summary", "")

#         if not summary:
#             response_message = "Relevant data is not available in the current analysis."
#         else:
#             # Keep answer concise (2–3 sentences)
#             sentences = summary.split(".")
#             response_message = ".".join(sentences[:3]).strip() + "."

#     # Store assistant response
#     session["chat_history"].append({
#         "sender": "master",
#         "message": response_message,
#         "timestamp": datetime.now().isoformat()
#     })

#     store_session(request.session_id, session)

#     return {
#         "response": response_message,
#         "sender": "master",
#         "agents_used": [selected_agent] if selected_agent else []
#     }
@app.post("/api/chat")
async def chat(request: ChatRequest):
    session = get_session(request.session_id)

    session["chat_history"].append({
        "sender": "user",
        "message": request.message,
        "timestamp": datetime.now().isoformat()
    })

    lower = request.message.lower()
    agent_results = session.get("agent_results", {})

    intent_map = {
        "iqvia": ["market", "sales", "cagr"],
        "exim": ["trade", "export", "import"],
        "trials": ["trial", "clinical", "phase"],
        "patents": ["patent", "fto", "ip"],
        "internal": ["internal", "strategy"],
        "web": ["web", "guideline", "news"]
    }

    selected_agent = None
    for agent, keys in intent_map.items():
        if any(k in lower for k in keys):
            selected_agent = agent
            break

    # READ ONLY
    if selected_agent and selected_agent in agent_results:
        summary = agent_results[selected_agent].get("summary", "")
        response = ". ".join(summary.split(".")[:3]).strip() + "."
    else:
        response = (
            "This question does not affect the data shown in the tabs. "
            "You can continue exploring the Market, Trade, Trials, and Patent tabs "
            "without any changes."
        )

    session["chat_history"].append({
        "sender": "master",
        "message": response,
        "timestamp": datetime.now().isoformat()
    })

    store_session(request.session_id, session)

    return {
        "response": response,
        "sender": "master"
    }

@app.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    """Get session data"""
    session = get_session(session_id)
    return {
        "molecule": session["molecule"],
        "agent_results": session.get("agent_results", {}),
        "chat_history": session.get("chat_history", []),
        "final_answer": session.get("final_answer", ""),
        "plan": session.get("plan", {}),
        "status": session.get("status", "processing")
    }

@app.get("/api/dossier/{session_id}")
async def get_dossier(session_id: str):
    """Get molecule dossier data"""
    session = get_session(session_id)
    agent_results = session.get("agent_results", {})
    
    # Extract data from agent results
    trials_data = agent_results.get("trials", {}).get("raw", {})
    patents_data = agent_results.get("patents", {}).get("raw", {})
    iqvia_data = agent_results.get("iqvia", {}).get("raw", {})
    
    # Format unmet needs (extract from summaries)
    unmet_needs = []
    for agent_key, result in agent_results.items():
        summary = result.get("summary", "")
        if summary:
            # Extract first few sentences
            sentences = summary.split('.')[:2]
            for sent in sentences:
                if len(sent.strip()) > 20:
                    unmet_needs.append(sent.strip() + ".")
    
    # Format innovation opportunities (placeholder - can be enhanced with LLM)
    innovation_opportunities = [
        {
            "title": "Extended-Release Formulation",
            "description": "Develop once-daily or once-weekly formulation to improve patient compliance",
            "feasibility": "High",
            "impact": "High"
        },
        {
            "title": "Fixed-Dose Combination",
            "description": "Combine with complementary mechanism of action for enhanced efficacy",
            "feasibility": "Medium",
            "impact": "High"
        },
        {
            "title": "Pediatric Formulation",
            "description": "Develop age-appropriate formulation for pediatric patients",
            "feasibility": "High",
            "impact": "Medium"
        },
        {
            "title": "Indication Expansion",
            "description": "Explore efficacy in related disease areas based on mechanism of action",
            "feasibility": "Medium",
            "impact": "Very High"
        }
    ]
    
    return {
        "molecule": session["molecule"],
        "unmet_needs": unmet_needs[:4],
        "trials": trials_data.get("active_trials", []),
        "patents": patents_data.get("patent_status", []),
        "innovation_opportunities": innovation_opportunities,
        "patient_stats": {
            "us_patients": "12.5M",
            "global_patients": "45M",
            "market_cagr": f"{iqvia_data.get('markets', [{}])[0].get('cagr_5y', '8.5')}%" if iqvia_data.get('markets') else "8.5%"
        }
    }

# @app.post("/api/generate-report")
# async def generate_report_integration(
#     report_type: str = Query("pdf", description="pdf or excel"),
#     topic: Optional[str] = Query(None, description="Report topic"),
#     session_id: Optional[str] = Query(None, description="Session ID (optional)")
# ):
#     """Generate report with session data or direct call (backward compatible)"""
#     session = None
    
#     # Try to get session if provided
#     if session_id:
#         try:
#             session = get_session(session_id)
#         except:
#             pass
    
#     # If no session_id but we have topic, try to find session by molecule name
#     if not session and topic:
#         # Extract molecule name from topic (e.g., "Semaglutide Innovation Opportunities")
#         topic_parts = topic.split()
#         if topic_parts:
#             molecule_name = topic_parts[0]
#             # Find most recent session with this molecule
#             for sid, sess in sessions.items():
#                 if sess.get("molecule", {}).get("name", "").lower() == molecule_name.lower():
#                     session = sess
#                     session_id = sid
#                     break
    
#     # If still no session, use a default for backward compatibility
#     if not session:
#         # Fallback: create minimal session data from topic
#         molecule_name = topic.split()[0] if topic else "Unknown"
#         session = {
#             "molecule": {"name": molecule_name, "indication": "General"},
#             "user_query": topic or "Innovation Opportunity Assessment",
#             "plan": {},
#             "agent_results": {},
#             "worker_results": []
#         }
    
#     # Get topic
#     if not topic and session:
#         molecule = session.get("molecule", {}).get("name", "Unknown")
#         indication = session.get("molecule", {}).get("indication", "General")
#         topic = f"Innovation Opportunity Assessment for {molecule} ({indication})"
#     elif not topic:
#         topic = "Innovation Opportunity Assessment"
    
#     # Prepare report data
#     report_data = {
#         "user_query": session.get("user_query", topic),
#         "plan": session.get("plan", {}),
#         "worker_results": session.get("worker_results", []),
#         "detailed_agent_responses": []
#     }
    
#     # Collect agent data
#     agent_results = session.get("agent_results", {})
#     for agent_key, result in agent_results.items():
#         agent_data = {
#             "agent_name": result.get("agent", agent_key),
#             "params": result.get("params", {}),
#             "summary": result.get("summary", ""),
#             "raw_json_response": result.get("raw", {})
#         }
#         report_data["detailed_agent_responses"].append(agent_data)
    
#     # Call report agent
#     master = MasterAgent()
#     include_sections = [
#         "Executive Summary",
#         "Market Analysis",
#         "EXIM / Sourcing",
#         "Clinical Pipeline",
#         "Patent Landscape",
#         "Internal Strategy Insights",
#         "Guidelines & Web Intelligence",
#         "Recommendations"
#     ]
    
#     # Prepare worker results
#     worker_results = session.get("worker_results", [])
#     if not worker_results and session.get("agent_results"):
#         # Convert agent_results to worker_results format
#         worker_results = list(session["agent_results"].values())
    
#     try:
#         report_result = master.report_agent.run(
#             topic=topic,
#             user_query=session.get("user_query", topic),
#             plan=session.get("plan", {}),
#             worker_results=worker_results,
#             include_sections=include_sections
#         )
        
#         # Store report_id in session if we have session_id
#         if session_id:
#             if session_id in sessions:
#                 sessions[session_id]["report_id"] = report_result["raw"].get("report_id")
            
#             # Also store in report_storage for PDF download
#             report_id = report_result["raw"].get("report_id")
#             if report_id:
#                 if report_id not in report_storage or "report_data" not in report_storage[report_id]:
#                     report_storage[report_id] = {
#                         "topic": topic,
#                         "report_data": report_data,
#                         "generated_at": datetime.now().isoformat()
#                     }
        
#         return report_result["raw"]
#     except Exception as e:
#         # Fallback to basic report generation
#         report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#         return {
#             "report_id": report_id,
#             "report_type": "PDF",
#             "topic": topic,
#             "status": "Generated",
#             "download_link": f"/downloads/reports/{report_id}.pdf",
#             "error": str(e)
#         }

@app.get("/api/reports")
async def list_reports():
    """List all saved reports"""
    reports = []
    for session_id, session in sessions.items():
        if "report_id" in session:
            reports.append({
                "report_id": session["report_id"],
                "session_id": session_id,
                "molecule": session["molecule"]["name"],
                "indication": session["molecule"]["indication"],
                "geography": session["molecule"]["geography"],
                "date": session.get("created_at", ""),
                "tags": [session["molecule"]["indication"]]  # Simple tag generation
            })
    
    # Sort by date (newest first)
    reports.sort(key=lambda x: x["date"], reverse=True)
    return reports

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get specific report data"""
    # Find session with this report_id
    for session_id, session in sessions.items():
        if session.get("report_id") == report_id:
            return {
                "report_id": report_id,
                "session": session,
                "download_link": f"/downloads/reports/{report_id}.pdf"
            }
    
    raise HTTPException(status_code=404, detail="Report not found")

# Import PDF generation function from mock_api
try:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from mock_api import generate_pdf_content, report_storage
except ImportError:
    # Fallback if import fails
    def generate_pdf_content(report_id, topic, report_data):
        return b"%PDF-1.4\n%Mock PDF\n"
    
    report_storage = {}

@app.get("/downloads/reports/{report_id}.pdf")
async def download_pdf_report_integration(report_id: str):
    """Serve PDF reports from report storage"""
    if report_id not in report_storage:
        return Response(
            content=json.dumps({"error": "Report not found"}).encode(),
            media_type="application/json",
            status_code=404
        )
    
    stored_data = report_storage[report_id]
    topic = stored_data.get("topic", "Pharma Innovation Assessment")
    report_data = stored_data.get("report_data", {})
    
    try:
        pdf_content = generate_pdf_content(report_id, topic, report_data)
    except Exception as e:
        # Fallback PDF
        pdf_content = f"%PDF-1.4\n1 0 obj<<</Type/Catalog>>endobj\nxref 0 1\ntrailer<</Size 1/Root 1 0 R>>startxref 50 %%EOF".encode()
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{report_id}.pdf"',
            "Content-Length": str(len(pdf_content))
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

