"""
Single File API for Behavior Intelligence MVP
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from datetime import datetime

# Import core logic
from features.rfm import calculate_rfm_scores
from segmentation.rfm_segments import assign_segment
from actions.action_engine import get_recommended_actions
from drift.segment_drift import calculate_drift
import config

app = FastAPI(title=config.app.name)

# --- In-Memory Data Store (Simplification for MVP) ---
# In real prod, this logic sits in a service or DB
def get_data_state():
    # Load transactions
    try:
        df = pd.read_csv(config.data.transactions_file)
    except FileNotFoundError:
        return None, None
    
    # Run Pipeline
    rfm = calculate_rfm_scores(df)
    rfm['segment'] = rfm.apply(lambda row: assign_segment(row['R'], row['F']), axis=1)
    
    return df, rfm

# --- Endpoints ---

@app.get("/segments")
def get_segments():
    _, rfm = get_data_state()
    if rfm is None:
        return {"error": "No data found"}
        
    counts = rfm['segment'].value_counts().to_dict()
    return counts

@app.get("/actions")
def get_actions():
    _, rfm = get_data_state()
    if rfm is None:
        return []
    
    all_actions = []
    
    # Generate actions for all customers
    # (In real world, paginate or filter)
    for _, row in rfm.iterrows():
        # Get actions for this customer
        acts = get_recommended_actions(
            customer_id=row.name, # index is customer_id
            segment=row['segment'],
            r=row['R'],
            f=row['F'],
            m=row['M'],
            score=row['rfm_score']
        )
        # Inject score into action objects for UI display
        for a in acts:
            a['score'] = row['rfm_score']
            
        all_actions.extend(acts)
        
    # Sort by priority using config map
    p_map = config.actions.priority_map
    all_actions.sort(key=lambda x: p_map.get(x['priority'], 99))
    
    return all_actions[:200]  # Return top 200 for UI

class FeedbackItem(BaseModel):
    action_id: str
    segment: str
    customer_id: str
    applied: str  # yes/no
    outcome: str = "unknown"

class BatchFeedbackItem(BaseModel):
    items: list[FeedbackItem]

@app.post("/feedback")
def save_feedback(item: FeedbackItem):
    _save_feedback_rows([item.dict()])
    return {"status": "saved"}

@app.post("/feedback/batch")
def save_batch_feedback(batch: BatchFeedbackItem):
    rows = [item.dict() for item in batch.items]
    _save_feedback_rows(rows)
    return {"status": "batch saved", "count": len(rows)}

def _save_feedback_rows(rows: list):
    file_path = config.data.feedback_file
    clean_rows = []
    
    for r in rows:
        clean_rows.append({
            'action_id': r['action_id'],
            'segment': r['segment'],
            'customer_id': r['customer_id'],
            'applied': r['applied'],
            'outcome': r.get('outcome', 'unknown'),
            'timestamp': datetime.now().isoformat()
        })
        
    df = pd.DataFrame(clean_rows)
    
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', header=False, index=False)

@app.get("/drift")
def get_drift():
    # Mocking 'previous' state for demo purposes as we don't have historical snapshots yet
    # In real app, load yesterday's stats from file/DB
    
    current_counts = get_segments()
    if "error" in current_counts:
        return []
        
    # Mock previous (just perturb current slightly)
    import random
    prev_counts = {k: max(0, v + random.randint(-5, 5)) for k,v in current_counts.items()}
    
    drift_df = calculate_drift(current_counts, prev_counts)
    return drift_df.to_dict(orient='records')

@app.get("/rfm-details")
def get_rfm_details():
    _, rfm = get_data_state()
    if rfm is None:
        return []
    return rfm.reset_index().to_dict(orient='records')

@app.get("/revenue-trends")
def get_revenue_trends():
    df, _ = get_data_state()
    if df is None:
        return []
    df['date'] = pd.to_datetime(df['date'])
    daily_rev = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_rev.columns = ['date', 'revenue']
    daily_rev['date'] = daily_rev['date'].apply(lambda x: x.isoformat())
    return daily_rev.to_dict(orient='records')
