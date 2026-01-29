"""
Shared Utilities
"""
import pandas as pd
import yaml
import os

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop duplicates and nulls."""
    df = df.copy()
    df = df.drop_duplicates()
    df = df.dropna()
    return df
