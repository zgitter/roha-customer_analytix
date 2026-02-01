"""
RFM Segmentation Logic
"""

def assign_segment(r: int, f: int, m: int = None) -> str:
    """
    Assigns segment based on R and F scores using rules from config.yaml.
    """
    import config
    
    # Iterate through segments defined in config
    # The order in yaml determines priority if ranges overlap
    for seg in config.rfm.segments:
        r_range = seg.get('r_range')
        f_range = seg.get('f_range')
        m_range = seg.get('m_range')
        
        # Check R
        if not (r_range[0] <= r <= r_range[1]):
            continue
            
        # Check F
        if not (f_range[0] <= f <= f_range[1]):
            continue
            
        # Check M (if defined in config and provided)
        if m_range and m is not None:
             if not (m_range[0] <= m <= m_range[1]):
                 continue
                 
        return seg['name']
        
    return "Needs Attention"
