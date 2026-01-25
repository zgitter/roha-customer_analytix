"""
Data Ingestion Script
"""
import pandas as pd
import yaml
import os
from pathlib import Path
from typing import Optional


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def ingest_csv(
    file_path: str,
    output_dir: Optional[str] = None,
    date_columns: list = None
) -> pd.DataFrame:
    """
    Ingest CSV file and save to cleaned directory.
    
    Parameters
    ----------
    file_path : str
        Path to input CSV file
    output_dir : str, optional
        Output directory for cleaned data
    date_columns : list, optional
        Columns to parse as dates
    """
    config = load_config()
    
    if output_dir is None:
        output_dir = config.get('data', {}).get('cleaned_dir', './data/cleaned')
    
    # Read CSV
    df = pd.read_csv(file_path, parse_dates=date_columns)
    
    print(f"Loaded {len(df)} rows from {file_path}")
    print(f"Columns: {list(df.columns)}")
    
    # Basic cleaning
    initial_rows = len(df)
    df = df.drop_duplicates()
    df = df.dropna(how='all')
    
    print(f"After cleaning: {len(df)} rows (removed {initial_rows - len(df)} duplicates/empty)")
    
    # Save cleaned data
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")
    
    return df


def generate_sample_data(n_customers: int = 500, n_transactions: int = 5000):
    """Generate sample transaction data for testing."""
    import numpy as np
    
    np.random.seed(42)
    config = load_config()
    
    # Generate customers
    customer_ids = [f'C{i:04d}' for i in range(n_customers)]
    
    # Generate transactions
    transactions = []
    for _ in range(n_transactions):
        customer_id = np.random.choice(customer_ids)
        date = pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365))
        amount = round(np.random.exponential(100) + 10, 2)
        
        transactions.append({
            'customer_id': customer_id,
            'transaction_date': date.strftime('%Y-%m-%d'),
            'amount': amount
        })
    
    df = pd.DataFrame(transactions)
    
    # Save to samples directory
    samples_dir = config.get('data', {}).get('samples_dir', './data/samples')
    Path(samples_dir).mkdir(parents=True, exist_ok=True)
    
    output_path = os.path.join(samples_dir, 'sample_transactions.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {n_transactions} sample transactions for {n_customers} customers")
    print(f"Saved to {output_path}")
    
    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Ingestion")
    parser.add_argument("--generate-sample", action="store_true", help="Generate sample data")
    parser.add_argument("--input", type=str, help="Input CSV file to ingest")
    
    args = parser.parse_args()
    
    if args.generate_sample:
        generate_sample_data()
    elif args.input:
        ingest_csv(args.input)
    else:
        print("Use --generate-sample to create test data or --input <file> to ingest CSV")
