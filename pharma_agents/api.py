# api.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from master_agent import MasterAgent

load_dotenv()

app = FastAPI(title="Agentic AI Demo API")

# Create ONE master agent instance
master_agent = MasterAgent()

class QueryRequest(BaseModel):
    user_query: str

@app.post("/run")
def run_agent(req: QueryRequest):
    """
    This replaces main.py for hosting
    """
    result = master_agent.run(req.user_query)
    return result

@app.get("/health")
def health():
    return {"status": "ok"}