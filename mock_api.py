from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/api/iqvia")
def get_iqvia(molecule: str):
    # In real world you would query IQVIA, here just dummy data
    if molecule.lower() == "metformin":
        return {
            "molecule": "Metformin",
            "markets": [
                {"country": "US", "sales_2024_musd": 800, "cagr_5y": 3.5},
                {"country": "India", "sales_2024_musd": 200, "cagr_5y": 7.2}
            ],
            "therapy_area": "Type 2 Diabetes",
            "unmet_need_flag": True
        }
    return {"molecule": molecule, "markets": []}