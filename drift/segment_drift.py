"""
Segment Drift Detection
"""
import pandas as pd

def calculate_drift(current_counts: dict, previous_counts: dict) -> pd.DataFrame:
    """
    Compares current segment percentages vs previous.
    
    current_counts: {'SegmentName': count, ...}
    previous_counts: {'SegmentName': count, ...}
    """
    
    # Calculate totals
    total_curr = sum(current_counts.values())
    total_prev = sum(previous_counts.values())
    
    # Helper for %
    def get_pct(count, total):
        return (count / total * 100) if total > 0 else 0
    
    drift_data = []
    
    # Union of all known segments
    all_segments = set(current_counts.keys()) | set(previous_counts.keys())
    
    for seg in all_segments:
        curr = current_counts.get(seg, 0)
        prev = previous_counts.get(seg, 0)
        
        curr_pct = get_pct(curr, total_curr)
        prev_pct = get_pct(prev, total_prev)
        
        change = curr_pct - prev_pct
        
        drift_data.append({
            "segment_name": seg,
            "previous_percentage": round(prev_pct, 1),
            "current_percentage": round(curr_pct, 1),
            "change": round(change, 1)
        })
        
    return pd.DataFrame(drift_data)
