"""
RFM Segmentation Logic
"""

def assign_segment(r: int, f: int) -> str:
    """
    Assigns segment based on R and F scores using hard-coded rules.
    
    | Segment             | R   | F   |
    | ------------------- | --- | --- |
    | Champions           | 4–5 | 4–5 |
    | Loyal               | 3–5 | 3–5 |
    | Potential Loyalists | 4–5 | 1–3 |
    | At Risk             | 1–2 | 3–5 |
    | Hibernating         | 1–2 | 1–2 |
    """
    
    # Logic is hierarchical - order matters or strict ranges needed
    
    if r in [4, 5] and f in [4, 5]:
        return "Champions"
    
    if r in [4, 5] and f in [1, 2, 3]:
        return "Potential Loyalists"
    
    # Overlap handling: Champions covered above. 
    # Use strict lower bound for Loyal to catch mid-range not caught by Champions.
    # Actually, purely based on the table:
    # Loyal is 3-5, 3-5. Champions is subset 4-5, 4-5.
    # To differentiate, we check Champions first.
    
    if r in [3, 4, 5] and f in [3, 4, 5]:
        return "Loyal"
        
    if r in [1, 2] and f in [3, 4, 5]:
        return "At Risk"
        
    if r in [1, 2] and f in [1, 2]:
        return "Hibernating"
        
    # Catch-all for gaps in the simple logic (e.g. R=3, F=1 or 2)
    return "Needs Attention"
