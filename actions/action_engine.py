"""
Action Engine - Rule-Based Recommendations
"""
from typing import List, Dict

def get_recommended_actions(customer_id: str, 
                          segment: str, 
                          r: int, 
                          f: int, 
                          m: int, 
                          score: float) -> List[Dict]:
    """
    Returns a list of action objects based on segment and scores.
    """
    actions = []
    
    # --- Rule 1: Retention ---
    # IF segment == "At Risk" AND M >= 4
    if segment == "At Risk" and m >= 4:
        actions.append({
            "action_id": "act_retention_001",
            "customer_id": customer_id,
            "segment": segment,
            "message": "Offer retention incentive",
            "reason": "High value customer showing declining activity",
            "priority": "High"
        })
        
    # --- Rule 2: Growth ---
    # IF segment == "Potential Loyalists"
    if segment == "Potential Loyalists":
        actions.append({
            "action_id": "act_growth_001",
            "customer_id": customer_id,
            "segment": segment,
            "message": "Encourage repeat purchase",
            "reason": "Recent customer with low frequency",
            "priority": "Medium"
        })
        
    # --- Rule 3: Loyalty ---
    # IF segment == "Champions"
    if segment == "Champions":
        actions.append({
            "action_id": "act_loyalty_001",
            "customer_id": customer_id,
            "segment": segment,
            "message": "Reward loyalty",
            "reason": "Top tier customer",
            "priority": "Low" # Low urgency, but high importance relationship w.r.t maintenance
        })
        
    return actions
