# start_server.py
# Unified server that combines mock_api and api_integration
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Import both apps
from mock_api import app as mock_app, report_storage as mock_report_storage
from api_integration import app as integration_app, sessions, active_websockets

# Create main app - use mock_app as base since it has all the agent endpoints
main_app = mock_app

# Share report storage between apps
import api_integration
api_integration.report_storage = mock_report_storage

# Import integration routes - need to import functions directly
import api_integration

# Add integration routes to main app
main_app.post("/api/orchestrate")(api_integration.orchestrate)

# WebSocket route - use the decorator syntax which is the correct way
@main_app.websocket("/ws/{session_id}")
async def websocket_handler(websocket: WebSocket, session_id: str):
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
main_app.post("/api/chat")(api_integration.chat)
main_app.get("/api/session/{session_id}")(api_integration.get_session_data)
main_app.get("/api/session/{session_id}/status")(api_integration.get_session_status)
main_app.get("/api/dossier/{session_id}")(api_integration.get_dossier)
main_app.post("/api/generate-report")(api_integration.generate_report_integration)
main_app.get("/api/reports")(api_integration.list_reports)
main_app.get("/api/reports/{report_id}")(api_integration.get_report)
main_app.get("/downloads/reports/{report_id}.pdf")(api_integration.download_pdf_report_integration)

if __name__ == "__main__":
    print("="*70)
    print("Starting PharmaVerse Unified API Server")
    print("="*70)
    print("Mock API endpoints: /api/iqvia, /api/exim, /api/patents, etc.")
    print("Integration endpoints:")
    print("  POST /api/orchestrate - Launch agent orchestration")
    print("  WS /ws/{session_id} - WebSocket for real-time updates")
    print("  POST /api/chat - Chat with master agent")
    print("  GET /api/session/{session_id} - Get session data")
    print("  GET /api/dossier/{session_id} - Get molecule dossier")
    print("  GET /api/reports - List all reports")
    print("  GET /downloads/reports/{report_id}.pdf - Download PDF")
    print("="*70)
    # Use import string to enable reload
    uvicorn.run("start_server:main_app", host="0.0.0.0", port=8000, reload=True)

