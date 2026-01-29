"""
RFM Computation Engine
"""
import pandas as pd
import numpy as np

def calculate_rfm_scores(df: pd.DataFrame, 
                         customer_col='customer_id', 
                         date_col='date', 
                         amount_col='amount') -> pd.DataFrame:
    """
    Computes R, F, M scores (1-5) and weighted composite score.
    Input df must have: customer_id, date, amount
    """
    # Defensive copy & conversion
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Snapshot date (max date + 1 day to ensure recency > 0)
    snapshot_date = df[date_col].max() + pd.Timedelta(days=1)
    
    # Aggregation
    rfm = df.groupby(customer_col).agg({
        date_col: lambda x: (snapshot_date - x.max()).days,
        customer_col: 'count',
        amount_col: 'sum'
    }).rename(columns={
        date_col: 'recency',
        customer_col: 'frequency',
        amount_col: 'monetary'
    })
    
    # Scoring (Quintiles 1-5)
    # Recency: Lower is better (reverse labels)
    rfm['R'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: Higher is better
    # Use rank(method='first') to handle ties in low-data volume cases
    rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    
    # Monetary: Higher is better
    rfm['M'] = pd.qcut(rfm['monetary'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    
    # Convert to integers
    rfm['R'] = rfm['R'].astype(int)
    rfm['F'] = rfm['F'].astype(int)
    rfm['M'] = rfm['M'].astype(int)
    
    # Composite Score
    # score = 0.3R + 0.3F + 0.4M
    rfm['rfm_score'] = (0.3 * rfm['R']) + (0.3 * rfm['F']) + (0.4 * rfm['M'])
    rfm['rfm_score'] = rfm['rfm_score'].round(2)
    
    return rfm
