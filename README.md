# RFM Analytics (MVP)

A Python-based customer segmentation platform using RFM (Recency, Frequency, Monetary) analysis.

## 🚀 Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Generate sample data
python scripts/ingest_data.py --generate-sample

# Run Dashboard
streamlit run app/dashboard.py
```

## 📁 Project Structure

```
customer-analytics/
├── data/               # Data storage
│   ├── raw/           # Raw data files
│   ├── cleaned/       # Processed data
│   └── samples/       # Test data
├── features/          # Feature engineering
│   ├── rfm.py         # RFM calculations
│   └── utils.py       # Utilities
├── app/               # Applications
│   ├── api.py         # FastAPI REST API
│   └── dashboard.py   # Streamlit dashboard
├── scripts/           # Utility scripts
│   └── ingest_data.py # Data ingestion
├── config.yaml        # Configuration
└── requirements.txt
```

## 🎯 RFM Pipeline

```
Transaction Data → RFM Calculation → Scoring → Segmentation → Dashboard
```

### Customer Segments

| Segment | Description |
|---------|-------------|
| **Champions** | Best customers (high R, F, M) |
| **Loyal** | Regular buyers with good scores |
| **Potential Loyalists** | Recent with growth potential |
| **At Risk** | Haven't purchased recently |
| **Hibernating** | Low activity across metrics |

## 🖥️ Running Applications

### Dashboard

```bash
streamlit run app/dashboard.py
```
Access: http://localhost:8501

### API

```bash
uvicorn app.api:app --reload
```
Access: http://localhost:8000/docs

## 📝 License

MIT
