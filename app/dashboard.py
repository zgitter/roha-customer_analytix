"""
Streamlit Dashboard - RFM Customer Segmentation
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
import os


# ============ Page Config ============

st.set_page_config(
    page_title="RFM Segmentation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============ Helper Functions ============

@st.cache_data
def load_config():
    """Load configuration."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


@st.cache_data
def load_transaction_data():
    """Load transaction data from samples directory."""
    config = load_config()
    sample_path = os.path.join(
        config.get('data', {}).get('samples_dir', './data/samples'),
        'sample_transactions.csv'
    )
    
    if os.path.exists(sample_path):
        return pd.read_csv(sample_path, parse_dates=['transaction_date'])
    return None


def calculate_rfm_data(df):
    """Calculate RFM metrics for the dashboard."""
    from features.rfm import calculate_rfm, score_rfm, segment_customers
    
    rfm_df = calculate_rfm(df)
    rfm_df = score_rfm(rfm_df)
    rfm_df = segment_customers(rfm_df)
    
    return rfm_df


# ============ Dashboard Layout ============

def main():
    # Sidebar
    st.sidebar.title("📊 RFM Analytics")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Customer Segmentation Dashboard**")
    st.sidebar.markdown("Analyze customers based on:")
    st.sidebar.markdown("- **R**ecency")
    st.sidebar.markdown("- **F**requency")
    st.sidebar.markdown("- **M**onetary value")
    
    # Load data
    df = load_transaction_data()
    
    if df is None:
        st.error("No transaction data found. Please run:")
        st.code("python scripts/ingest_data.py --generate-sample")
        return
    
    # Calculate RFM
    rfm_df = calculate_rfm_data(df)
    
    # Main content
    show_rfm_dashboard(rfm_df)


def show_rfm_dashboard(df):
    """Show RFM segmentation dashboard."""
    st.title("📊 RFM Customer Segmentation")
    
    # KPI Cards
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(df))
    
    with col2:
        avg_recency = df['recency'].mean()
        st.metric("Avg Recency (days)", f"{avg_recency:.0f}")
    
    with col3:
        avg_frequency = df['frequency'].mean()
        st.metric("Avg Frequency", f"{avg_frequency:.1f}")
    
    with col4:
        avg_monetary = df['monetary'].mean()
        st.metric("Avg Monetary", f"${avg_monetary:,.0f}")
    
    st.markdown("---")
    
    # Segment Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Segments")
        segment_counts = df['segment'].value_counts()
        fig = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Revenue by Segment")
        segment_revenue = df.groupby('segment')['monetary'].sum().sort_values(ascending=True)
        fig = px.bar(
            x=segment_revenue.values,
            y=segment_revenue.index,
            orientation='h',
            color=segment_revenue.values,
            color_continuous_scale='Viridis',
            labels={'x': 'Total Revenue', 'y': 'Segment'}
        )
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # RFM Scatter Plot
    st.subheader("RFM Analysis")
    fig = px.scatter(
        df,
        x='recency',
        y='frequency',
        size='monetary',
        color='segment',
        hover_data=['customer_id', 'monetary', 'R_score', 'F_score', 'M_score'],
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={'recency': 'Recency (days)', 'frequency': 'Frequency'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment Statistics Table
    st.subheader("Segment Statistics")
    segment_stats = df.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': ['mean', 'sum']
    }).round(2)
    segment_stats.columns = ['Count', 'Avg Recency', 'Avg Frequency', 'Avg Monetary', 'Total Revenue']
    st.dataframe(segment_stats, use_container_width=True)
    
    # Customer Data Table
    st.subheader("Customer Details")
    segment_filter = st.selectbox(
        "Filter by Segment",
        ['All'] + list(df['segment'].unique())
    )
    
    if segment_filter == 'All':
        display_df = df
    else:
        display_df = df[df['segment'] == segment_filter]
    
    st.dataframe(
        display_df[['customer_id', 'recency', 'frequency', 'monetary', 'R_score', 'F_score', 'M_score', 'segment']].head(50),
        use_container_width=True
    )


if __name__ == "__main__":
    main()
