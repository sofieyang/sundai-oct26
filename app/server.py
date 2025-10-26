import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

import sys
from pathlib import Path

# Add project root to path so we can import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.marketing_agency import build_marketing_pipeline, deploy_markdown


class RfpRequest(BaseModel):
    companyUrl: HttpUrl
    drugName: str
    trialsPapers: str 
    doctorTypes: str
    brief: str


app = FastAPI(title="Sundai API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/rfp")
def submit_rfp(payload: RfpRequest) -> Dict[str, Any]:
    pipeline = build_marketing_pipeline()

    brief_text = payload.brief or (
        f"Company: {payload.companyUrl}\nDrug: {payload.drugName}\n"
        f"Doctor types: {payload.doctorTypes or '-'}\nTrials/Papers: {payload.trialsPapers or '-'}"
    )

    inputs = {"brief": brief_text}
    defaults = {
        "brand": "Acme Bio",
        "region": "US",
        "objective": "Generate HCP awareness",
    }

    try:
        print("[API] Starting marketing pipeline for RFP…")
        result = pipeline.run({
            "inputs": inputs,
            "pipeline": {"defaults": defaults},
        })
        print("[API] Pipeline completed. Preparing deployment artifact…")
        out_path = deploy_markdown({
            "inputs": inputs,
            "state": result if isinstance(result, dict) else {},
        }, output_path=os.path.abspath("deploy_output.md"))
        return {"ok": True, "result": result, "deploy_path": out_path}
    except Exception as e:
        print(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"ok": True}

# Uvicorn entry: uvicorn app.server:app --reload


