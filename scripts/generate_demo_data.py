"""
Demo Data Generator for Testing end-to-end flow
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_transactions(num_customers=500, num_txns=2000):
    """Generates customer_id, date, amount CSV"""
    
    # Customers
    c_ids = [f"C{str(i).zfill(3)}" for i in range(1, num_customers+1)]
    
    # Transaction data
    data = []
    
    # Ensure some variety for segments
    # High value group
    for _ in range(int(num_txns * 0.4)):
        c_id = np.random.choice(c_ids[:100]) # First 100 are potential high value
        date = datetime.now() - timedelta(days=np.random.randint(0, 30))
        amt = np.random.randint(100, 500)
        data.append([c_id, date, amt])
        
    # Churning group
    for _ in range(int(num_txns * 0.3)):
        c_id = np.random.choice(c_ids[100:300]) 
        date = datetime.now() - timedelta(days=np.random.randint(60, 120))
        amt = np.random.randint(20, 100)
        data.append([c_id, date, amt])
        
    # Recent low freq group
    for _ in range(int(num_txns * 0.3)):
        c_id = np.random.choice(c_ids[300:]) 
        date = datetime.now() - timedelta(days=np.random.randint(0, 10))
        amt = np.random.randint(10, 50)
        data.append([c_id, date, amt])
        
    df = pd.DataFrame(data, columns=['customer_id', 'date', 'amount'])
    
    print(f"Generated {len(df)} transactions for {num_customers} customers.")
    return df

if __name__ == "__main__":
    os.makedirs('data/raw', exist_ok=True)
    df = generate_transactions()
    df.to_csv('data/raw/demo_transactions.csv', index=False)
    print("Saved to data/raw/demo_transactions.csv")
