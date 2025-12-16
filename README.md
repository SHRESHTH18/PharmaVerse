# PharmaVerse - Agentic AI for Portfolio Innovation

## Overview
PharmaVerse is a comprehensive web application that uses AI agents to analyze pharmaceutical innovation opportunities. The system orchestrates multiple specialized AI agents to gather market intelligence, clinical trial data, patent information, and trade insights, then synthesizes this information into actionable innovation opportunities.

## Features

### 1. **Landing Page (Screen 1)**
- **Agent Network Visualization**: Interactive circular diagram showing the Master Agent at the center with 7 worker agents positioned around it
  - Internal Knowledge Agent
  - EXIM Trends Agent
  - Patent Landscape Agent
  - Clinical Trials Agent
  - IQVIA Insights Agent
  - Web Intelligence Agent
  - Report Generator Agent
- **Navigation Options**:
  - "Start New Molecule Exploration" - Initiates a new case analysis
  - "View Saved Cases / Reports" - Accesses archived reports

### 2. **Case Setup Screen (Screen 2)**
- **Input Form Fields**:
  - Molecule Name (e.g., Roflumilast)
  - Current Indication (e.g., COPD)
  - Geography (e.g., US, EU, India)
  - Target Timeframe (e.g., 2024-2026)
  - Strategic Question (free text)
- **Exploration Journey Visualization**: Shows 5-step process:
  1. Unmet Need & Disease Burden
  2. Market & EXIM Dynamics
  3. Clinical Trials Landscape
  4. Patent Landscape
  5. Product Story & Report
- **Launch Agent Run**: Triggers agent orchestration

### 3. **Main Workspace (Screen 3)**
- **Top Bar**:
  - Current molecule name and indication display
  - Navigation to Molecule Dossier
  - Report Generation button
- **Agent Status Strip**: Real-time status indicators for all agents
  - States: Idle, Running, Done, Error
  - Visual icons and animations
- **Left Sidebar**:
  - Case Details (Molecule, Indication, Geography)
  - Filters (Country dropdown, Therapy Area dropdown)
  - Conversation History list
- **Center: Chat Interface**:
  - Real-time chat messages from Master Agent and Worker Agents
  - User input field with send button
  - Message bubbles with agent-specific styling
  - Scrollable message history
- **Right Panel: Insights Tabs**:
  - **Overview Tab**: Executive summary and key findings
  - **Market Tab**: Market analysis with tables and charts
  - **Trade Tab**: EXIM data visualization
  - **Trials Tab**: Clinical trials pipeline information
  - **Patents Tab**: Patent landscape and FTO status

### 4. **Molecule Dossier (Screen 4)**
- **Header Section**: Molecule name, primary indication, and key unmet need
- **Unmet Needs & Patient Burden**:
  - Bulleted list of unmet needs
  - Patient statistics (US, Global, Market CAGR)
- **Ongoing Clinical Trials Table**:
  - Sponsor, Phase, Indication, Geography, Est. Completion
- **Patent Landscape Table**:
  - Assignee, Patent ID, Title, Expiry, FTO Flag
- **Innovation Opportunities**:
  - Grid of innovation idea cards with:
    - Title and description
    - Feasibility and Impact badges

### 5. **Reports Archive (Screen 5)**
- **Report Preview Section**:
  - Executive Summary
  - Market & EXIM Snapshot
  - Clinical Pipeline Overview
  - Patent Summary
  - Innovation Opportunities
  - Download buttons (PDF, Excel)
- **Report Archive Sidebar**:
  - List of saved reports
  - Molecule name, date, geography
  - Tags (Diabetes, Oncology, etc.)

### 6. **Agent Orchestration**
- Sequential execution of worker agents:
  1. IQVIA Agent (Market analysis)
  2. EXIM Agent (Trade data)
  3. Patent Agent (IP landscape)
  4. Clinical Trials Agent (Pipeline data)
  5. Web Intelligence Agent (Guidelines & publications)
- Master Agent coordination and chat responses

### 7. **Chat Functionality**
- Interactive chat with Master Agent
- Natural language query processing
- Keyword-based routing to specific agents
- Context-aware responses
- Multi-agent conversation flow

### 8. **Real-time Updates**
- Agent status animations (running pulse effect)
- Dynamic data loading in insight panels
- Live chat message updates
- Tab switching with context preservation

### 9. **Data Visualization**
- Tables for market, trade, trials, and patents data
- Charts for phase distribution (Clinical Trials)
- Summary cards with key metrics
- Badge indicators for status (Active, Clear, Blocked)

### 10. **Report Generation**
- PDF report generation
- Excel export option
- Report metadata (ID, date, topic)
- Download functionality

## Technology Stack
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: Tailwind CSS, Custom CSS animations
- **Charts**: Chart.js (included but not fully implemented)
- **Icons**: Font Awesome 6.4.0
- **API Integration**: Fetch API for REST endpoints

## UI/UX Features
- Gradient backgrounds and glass-morphism effects
- Smooth animations and transitions
- Responsive design (mobile-friendly)
- Custom scrollbars
- Loading spinners
- Hover effects on interactive elements
- Color-coded agent status indicators
- Tab-based navigation
- Modal-like screen transitions
