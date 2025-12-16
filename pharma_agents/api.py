

# api.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from master_agent import MasterAgent

load_dotenv()

app = FastAPI(title="Agentic AI Demo API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (use specific origins in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"],  # Allows all headers
)

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