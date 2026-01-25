"""
Feature Engineering Utilities
"""
import pandas as pd
import numpy as np
from typing import Optional


def load_config(config_path: str = "config.yaml") -> dict:
    """Load YAML configuration file."""
    import yaml
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Basic DataFrame cleaning operations."""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.dropna(subset=['customer_id'])
    
    return df


def calculate_date_diff(
    df: pd.DataFrame,
    date_col: str,
    reference_date: Optional[pd.Timestamp] = None
) -> pd.Series:
    """Calculate days difference from reference date."""
    if reference_date is None:
        reference_date = pd.Timestamp.now()
    
    return (reference_date - pd.to_datetime(df[date_col])).dt.days
