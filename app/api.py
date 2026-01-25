"""
FastAPI Application - RFM Analytics API
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import yaml

app = FastAPI(
    title="RFM Analytics API",
    description="API for RFM customer segmentation",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Pydantic Models ============

class CustomerTransaction(BaseModel):
    customer_id: str
    transaction_date: str
    amount: float


class RFMRequest(BaseModel):
    transactions: List[CustomerTransaction]


# ============ Helper Functions ============

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


# ============ API Endpoints ============

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RFM Analytics API"}


@app.get("/config")
async def get_config():
    """Get current configuration."""
    return load_config()


@app.post("/rfm/calculate")
async def calculate_rfm_endpoint(request: RFMRequest):
    """Calculate RFM scores for customers."""
    from features.rfm import calculate_rfm, score_rfm, segment_customers
    
    # Convert to DataFrame
    data = [t.model_dump() for t in request.transactions]
    df = pd.DataFrame(data)
    
    # Calculate RFM
    rfm_df = calculate_rfm(df)
    rfm_df = score_rfm(rfm_df)
    rfm_df = segment_customers(rfm_df)
    
    return rfm_df.to_dict(orient='records')


@app.get("/rfm/segments")
async def get_segment_definitions():
    """Get RFM segment definitions."""
    return {
        "segments": [
            {"name": "Champions", "description": "Best customers, high R, F, M"},
            {"name": "Loyal", "description": "Regular buyers with good scores"},
            {"name": "Potential Loyalists", "description": "Recent customers with potential"},
            {"name": "At Risk", "description": "Haven't purchased recently"},
            {"name": "Hibernating", "description": "Low activity across all metrics"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    config = load_config()
    uvicorn.run(
        "api:app",
        host=config.get("api", {}).get("host", "0.0.0.0"),
        port=config.get("api", {}).get("port", 8000),
        reload=config.get("api", {}).get("reload", True)
    )
