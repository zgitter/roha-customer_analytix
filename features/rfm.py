"""
RFM (Recency, Frequency, Monetary) Feature Engineering
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from .utils import load_config


def calculate_rfm(
    df: pd.DataFrame,
    customer_id_col: str = 'customer_id',
    date_col: str = 'transaction_date',
    amount_col: str = 'amount',
    reference_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Calculate RFM metrics for each customer.
    
    Parameters
    ----------
    df : pd.DataFrame
        Transaction data with customer_id, date, and amount
    customer_id_col : str
        Column name for customer ID
    date_col : str
        Column name for transaction date
    amount_col : str
        Column name for transaction amount
    reference_date : pd.Timestamp, optional
        Reference date for recency calculation (defaults to max date in data)
    
    Returns
    -------
    pd.DataFrame
        DataFrame with customer_id, recency, frequency, monetary columns
    """
    if reference_date is None:
        reference_date = pd.to_datetime(df[date_col]).max()
    
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    rfm = df.groupby(customer_id_col).agg({
        date_col: lambda x: (reference_date - x.max()).days,  # Recency
        customer_id_col: 'count',  # Frequency
        amount_col: 'sum'  # Monetary
    }).rename(columns={
        date_col: 'recency',
        customer_id_col: 'frequency',
        amount_col: 'monetary'
    })
    
    return rfm.reset_index()


def score_rfm(
    rfm_df: pd.DataFrame,
    n_bins: int = 5
) -> pd.DataFrame:
    """
    Assign RFM scores (1-5) to each customer.
    
    Parameters
    ----------
    rfm_df : pd.DataFrame
        DataFrame with recency, frequency, monetary columns
    n_bins : int
        Number of bins for scoring (default 5)
    
    Returns
    -------
    pd.DataFrame
        DataFrame with R_score, F_score, M_score, RFM_score columns added
    """
    df = rfm_df.copy()
    
    # Recency: lower is better
    df['R_score'] = pd.qcut(df['recency'], q=n_bins, labels=range(n_bins, 0, -1), duplicates='drop')
    
    # Frequency: higher is better
    df['F_score'] = pd.qcut(df['frequency'].rank(method='first'), q=n_bins, labels=range(1, n_bins + 1), duplicates='drop')
    
    # Monetary: higher is better
    df['M_score'] = pd.qcut(df['monetary'].rank(method='first'), q=n_bins, labels=range(1, n_bins + 1), duplicates='drop')
    
    # Combined RFM score
    df['RFM_score'] = df['R_score'].astype(str) + df['F_score'].astype(str) + df['M_score'].astype(str)
    
    return df


def segment_customers(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign customer segments based on RFM scores.
    """
    df = rfm_df.copy()
    
    def assign_segment(row):
        r, f, m = int(row['R_score']), int(row['F_score']), int(row['M_score'])
        
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r >= 4 and f <= 2:
            return 'New Customers'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        else:
            return 'Potential Loyalists'
    
    df['segment'] = df.apply(assign_segment, axis=1)
    return df
