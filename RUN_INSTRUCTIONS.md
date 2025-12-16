# PharmaVerse - Run Instructions

## Quick Start

### 1. Start the Unified API Server

```bash
python start_server.py
```

This will start the server on `http://localhost:8000` with:
- All mock API endpoints (for direct agent calls)
- All integration endpoints (for orchestration)
- WebSocket support for real-time updates

### 2. Open the Frontend

Open `website/index.html` in your browser or serve it with a local server:

```bash
# Option 1: Using Python
cd website
python -m http.server 8080

# Option 2: Using Node.js (if you have http-server installed)
npx http-server website -p 8080
```

Then navigate to `http://localhost:8080`

### 3. How It Works

**Current Frontend Behavior:**
- The frontend calls individual API endpoints (`/api/iqvia`, `/api/exim`, etc.) directly
- This works immediately with the existing `mock_api.py` endpoints
- All agent status updates and data display work as expected

**Enhanced Functionality (Optional - via WebSocket):**
- The backend now supports `/api/orchestrate` endpoint
- WebSocket connections at `/ws/{session_id}` for real-time updates
- You can enhance the frontend later to use orchestration without modifying core structure

## Features That Work Out of the Box

✅ **Landing Page** - Agent network visualization  
✅ **Case Setup** - Form input and navigation  
✅ **Main Workspace** - Chat interface and agent status  
✅ **Agent Execution** - Individual agents call mock API endpoints  
✅ **Insights Panels** - Data displays in tabs (Market, Trade, Trials, Patents)  
✅ **Molecule Dossier** - Comprehensive molecule view  
✅ **Report Generation** - PDF download functionality  
✅ **Chat Functionality** - User can send messages (enhanced with `/api/chat`)  

## API Endpoints Available

### Mock API Endpoints (Already Working)
- `GET /api/iqvia?molecule=...`
- `GET /api/exim?product=...`
- `GET /api/patents?molecule=...`
- `GET /api/clinical-trials?molecule=...`
- `GET /api/internal-knowledge?topic=...`
- `GET /api/web-intelligence?query=...`
- `POST /api/generate-report?report_type=pdf&topic=...`

### Integration Endpoints (New - For Enhanced Features)
- `POST /api/orchestrate` - Launch full agent orchestration
- `WS /ws/{session_id}` - WebSocket for real-time updates
- `POST /api/chat` - Enhanced chat with master agent
- `GET /api/session/{session_id}` - Get session data
- `GET /api/session/{session_id}/status` - Poll session status
- `GET /api/dossier/{session_id}` - Get molecule dossier data
- `GET /api/reports` - List all saved reports
- `GET /downloads/reports/{report_id}.pdf` - Download generated PDF

## Notes

- The frontend is **unchanged** and works with existing endpoints
- Backend provides both direct API calls and orchestration
- All features function smoothly with proper data flow
- PDF generation includes all agent responses in bullet points
- Real-time updates available via WebSocket (optional enhancement)

