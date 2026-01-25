# RFM Analytics — Project Documentation

> A customer segmentation platform built on the RFM (Recency, Frequency, Monetary) framework

---

## Project Architecture

### Layer Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│         Streamlit Dashboard  │  FastAPI REST API                │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      FEATURE ENGINEERING                         │
│                    RFM Calculation & Scoring                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                         DATA LAYER                               │
│              Raw Data  │  Cleaned Data  │  Samples               │
└─────────────────────────────────────────────────────────────────┘
```

---

### Layer 1: Data Layer

Storage layer for all transactional data.

| Directory | Purpose |
|-----------|---------|
| `data/raw/` | Original client data (CSV, exports) |
| `data/cleaned/` | Validated, deduplicated datasets |
| `data/samples/` | Synthetic test data for development |

**The Simplest Required Data Schema:**
```
customer_id, transaction_date, amount
C001, 2025-03-15, 150.00
C001, 2025-06-22, 89.50
C002, 2025-01-10, 220.00
```

---

### Layer 2: Feature Engineering Layer

Transforms raw transactions into RFM metrics.

| File | Purpose |
|------|---------|
| `features/rfm.py` | RFM calculation, scoring, segmentation |
| `features/utils.py` | Config loading, data utilities |

**Functions:**
- `calculate_rfm()` — Aggregate transactions to R, F, M values
- `score_rfm()` — Assign 1-5 scores using quintiles
- `segment_customers()` — Map scores to business segments

---

### Layer 3: Presentation Layer

User-facing interfaces for analytics.

| File | Purpose | Access |
|------|---------|--------|
| `app/dashboard.py` | Interactive Streamlit dashboard | `localhost:8501` |
| `app/api.py` | REST API for programmatic access | `localhost:8000` |

---

## RFM Pipeline

### What is RFM?

RFM is a customer segmentation technique based on three behavioral metrics:

| Metric | Definition | Scoring |
|--------|------------|---------|
| **Recency** | Days since last purchase | Lower = Better (5) |
| **Frequency** | Total number of purchases | Higher = Better (5) |
| **Monetary** | Total amount spent | Higher = Better (5) |

### Pipeline Flow

```
┌──────────────────┐
│ Transaction Data │
│ (CSV)            │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ calculate_rfm()  │
│ • Group by       │
│   customer_id    │
│ • Compute R,F,M  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ score_rfm()      │
│ • Quintile bins  │
│ • R_score (1-5)  │
│ • F_score (1-5)  │
│ • M_score (1-5)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ segment_         │
│ customers()      │
│ • Rule-based     │
│   assignment     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Customer         │
│ Segments         │
└──────────────────┘
```

### Segment Definitions

| Segment | R Score | F Score | Action |
|---------|---------|---------|--------|
| **Champions** | 4-5 | 4-5 | Reward & retain |
| **Loyal** | 3-5 | 3-5 | Upsell opportunities |
| **Potential Loyalists** | 4-5 | 1-3 | Nurture relationship |
| **At Risk** | 1-2 | 3-5 | Urgent re-engagement |
| **Hibernating** | 1-2 | 1-2 | Win-back campaigns |

---

## Next Steps

### Immediate Priorities

1. **Real Data Integration**
   - Connect to actual transaction source
   - Implement data validation
   - Add preprocessing pipeline

2. **Data Quality**
   - Handle missing values
   - Detect/remove outliers
   - Standardize date formats

3. **Enhanced Segmentation**
   - Add K-Means clustering option
   - Time-based segment evolution tracking

---

### Minimum Required Fields

```python
# Essential columns
required_columns = [
    'customer_id',       # Unique customer identifier
    'transaction_date',  # Date of purchase (YYYY-MM-DD)
    'amount'             # Transaction value (numeric)
]

# Helpful additions
optional_columns = [
    'transaction_id',    # Unique transaction ID
    'product_category',  # For category-level RFM
    'channel',           # Online, Store, Mobile
]
```

---

## Data Pipeline Requirements

To prepare real data for RFM analysis, implement these preprocessing steps:

### 1. Data Ingestion

```python
# scripts/ingest_data.py should handle:
- Load from CSV, API, or database
- Validate required columns exist
- Parse dates consistently
- Save to data/raw/
```

### 2. Data Cleaning

```python
# Cleaning operations needed:
- Remove duplicate transactions
- Handle null customer_ids (drop)
- Handle null amounts (drop or impute)
- Convert dates to datetime
- Filter date range (e.g., last 12 months)
```

### 3. Data Validation

```python
# Validation checks:
- amount > 0 (exclude refunds or filter separately)
- transaction_date <= today (no future dates)
- customer_id not empty
- Remove test transactions
```

### 4. Data Transformation

```python
# Prepare for RFM:
- Aggregate to customer level
- Set reference date (analysis date)
- Calculate days since last purchase
- Sum frequencies and monetary values
```

### Suggested Pipeline Structure

```
data/raw/transactions.csv
        │
        ▼
┌───────────────────┐
│ 1. INGEST         │
│ • Load file       │
│ • Validate schema │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 2. CLEAN          │
│ • Remove nulls    │
│ • Remove dupes    │
│ • Parse dates     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 3. VALIDATE       │
│ • Check ranges    │
│ • Flag anomalies  │
└─────────┬─────────┘
          │
          ▼
data/cleaned/transactions_clean.csv
          │
          ▼
┌───────────────────┐
│ 4. RFM PIPELINE   │
│ • calculate_rfm() │
│ • score_rfm()     │
│ • segment()       │
└─────────┬─────────┘
          │
          ▼
      Dashboard
```

---

## Running the Project

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Generate sample data (for testing)
python scripts/ingest_data.py --generate-sample

# 3. Launch dashboard
streamlit run app/dashboard.py

# 4. Or launch API
uvicorn app.api:app --reload
```

---

## Configuration

All settings in `config.yaml`:

(The values in the config file are based on the classic RFM marketing framework)

```yaml
data:
  raw_dir: "./data/raw"
  cleaned_dir: "./data/cleaned"
  samples_dir: "./data/samples"

rfm:
  n_bins: 5  # Quintile scoring
  recency_weight: 0.3
  frequency_weight: 0.3
  monetary_weight: 0.4
```
