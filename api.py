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

app = FastAPI(title="Behavior Intelligence API")

# --- In-Memory Data Store (Simplification for MVP) ---
# In real prod, this logic sits in a service or DB
def get_data_state():
    # Load transactions
    try:
        df = pd.read_csv('data/raw/demo_transactions.csv')
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
        all_actions.extend(acts)
        
    # Sort by priority (Hack: string sort works High > Medium > Low roughly, but let's be explicit)
    # Actually 'High' < 'Medium' alphanumerically? No.
    # Map priority to int
    p_map = {'High': 0, 'Medium': 1, 'Low': 2}
    all_actions.sort(key=lambda x: p_map.get(x['priority'], 99))
    
    return all_actions[:50] # Return top 50 for UI

class FeedbackItem(BaseModel):
    action_id: str
    segment: str
    applied: str # yes/no
    outcome: str = "unknown"

@app.post("/feedback")
def save_feedback(item: FeedbackItem):
    file_path = 'data/feedback.csv'
    
    # Prepare row
    row = {
        'action_id': item.action_id,
        'segment': item.segment,
        'applied': item.applied,
        'outcome': item.outcome,
        'timestamp': datetime.now().isoformat()
    }
    
    df = pd.DataFrame([row])
    
    # Append
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode='a', header=False, index=False)
        
    return {"status": "saved"}

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
