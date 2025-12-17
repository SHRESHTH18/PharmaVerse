

# PharmaVerse  
### Agentic AI Platform for Pharmaceutical Portfolio Innovation

---

## 🚩 Problem Statement

Pharmaceutical innovation decisions require synthesizing insights from **multiple fragmented data sources**—market intelligence, clinical trials, patents, trade flows, and scientific guidelines.  
Today, this process is **manual, time-consuming, and siloed**, making it difficult for strategy and R&D teams to identify high-value innovation opportunities quickly.

**PharmaVerse** addresses this challenge by using **Agentic AI** to autonomously collect, analyze, and integrate diverse pharma intelligence into a **single, explainable, and actionable workflow**.

---

## 💡 Solution Overview

PharmaVerse is a **multi-agent AI system** that:
- Orchestrates domain-specific AI agents
- Maintains structured, persistent insights
- Enables natural language interaction
- Produces **decision-ready dashboards and downloadable reports**

The platform transforms a **single strategic question** into:
- Cross-functional insights
- Interactive analysis tabs
- A professionally structured PDF report

---

## 🧠 System Architecture
User (Web UI)
│
▼
Master Agent (LLM + LangGraph)
│
├── IQVIA Agent        → Market & competition
├── EXIM Agent         → Trade & sourcing
├── Patent Agent       → IP & FTO
├── Clinical Agent     → Trial pipeline
├── Web Intel Agent    → Guidelines & publications
├── Internal Agent     → Strategy insights
├── Demographic Agent  → Chart-ready data
└── Report Agent       → PDF generation

---

## 🔄 End-to-End Workflow

### 1️⃣ Case Setup
User provides:
- Molecule
- Indication
- Geography
- Timeframe
- Strategic question

---

### 2️⃣ Agent Planning (LLM-Driven)
The **Master Agent**:
- Interprets the user intent
- Determines which agents to invoke
- Extracts molecule & indication context

---

### 3️⃣ Agent Execution
Each agent:
- Operates independently
- Fetches domain-specific intelligence
- Returns structured JSON + concise summary

Outputs are **cached** and reused throughout the session.

---

### 4️⃣ Interactive Workspace

#### Chat Interface
- Natural language interaction
- Master Agent synthesizes insights
- Follow-up questions answered without re-running agents

#### Insights Tabs (Persistent & Independent)
- Overview
- Market
- Trade
- Clinical Trials
- Patents

> Follow-up questions **never overwrite tab data**

---

### 5️⃣ Report Generation
- Report generated **once per analysis**
- Includes:
  - Executive summary
  - Agent insights
  - Demographic charts
- Same download link reused across:
  - Chat window
  - Innovation Opportunity screen
  - Download PDF button

---

## 📊 Key Features

- Multi-agent orchestration
- LLM-driven planning
- Structured & explainable outputs
- Persistent UI state
- Follow-up safe interaction
- Automated PDF report generation

---

## 🛠️ Technology Stack

### Frontend
- HTML5
- Vanilla JavaScript
- Tailwind CSS
- Font Awesome
- Chart.js

### Backend
- Python 3.9+
- FastAPI
- LangChain
- LangGraph
- Groq LLM
- ReportLab
- Matplotlib

---

---

## 🎯 Hackathon Value Proposition

- Demonstrates **real-world Agentic AI**
- Clear separation of reasoning & execution
- Scalable, modular architecture
- Enterprise-ready decision support system
- Strong alignment with pharma strategy workflows

---

## 🚀 Future Enhancements

- User authentication & saved sessions
- Multi-molecule comparison
- Real-time external data connectors
- Advanced dashboards
- Role-based insights

---

## PharmaVerse  
**From fragmented pharma intelligence to innovation-ready decisions — powered by Agentic AI.**
