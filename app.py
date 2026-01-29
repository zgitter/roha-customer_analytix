"""
Multi-Tab Dashboard - Action Center & Analytics Deep Dive
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import requests
import altair as alt
import plotly.express as px

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Action Center & Analytics", layout="wide")

# --- Helper to fetch data ---
def fetch_api(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        return r.json()
    except:
        return None

# --- Main Layout ---
st.title("Behavior Intelligence Platform")

tab1, tab2 = st.tabs(["🎯 Action Center", "📈 Analytics Deep Dive"])

# =================================================================
# TAB 1: ACTION CENTER
# =================================================================
with tab1:
    st.header("⚠️ High Priority Actions")
    
    actions = fetch_api("actions")
    
    if actions:
        cols = st.columns(3)
        for i, action in enumerate(actions[:3]):
            with cols[i]:
                with st.container(border=True):
                    st.subheader(f"{action['priority']} Priority")
                    st.markdown(f"**Segment:** {action['segment']}")
                    st.info(f"📢 {action['message']}")
                    st.caption(f"Reason: {action['reason']}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Apply", key=f"yes_{i}"):
                        requests.post(f"{API_URL}/feedback", json={
                            "action_id": action['action_id'],
                            "segment": action['segment'],
                            "applied": "yes"
                        })
                        st.toast("Action Applied!")
                        
                    if c2.button("❌ Ignore", key=f"no_{i}"):
                        requests.post(f"{API_URL}/feedback", json={
                            "action_id": action['action_id'],
                            "segment": action['segment'],
                            "applied": "no"
                        })
                        st.toast("Action Ignored")
    else:
        st.warning("API Offline or No Actions Found")

    st.divider()
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.header("Segment Overview")
        segments = fetch_api("segments")
        if segments and "error" not in segments:
            seg_df = pd.DataFrame(list(segments.items()), columns=['Segment', 'Count'])
            chart = alt.Chart(seg_df).mark_bar().encode(
                x='Count',
                y=alt.Y('Segment', sort='-x'),
                color='Segment'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No segment data available")
            
    with col_b:
        st.header("Segment Drift (Last 24h)")
        drift = fetch_api("drift")
        if drift:
            drift_df = pd.DataFrame(drift)
            st.dataframe(drift_df.style.background_gradient(subset=['change'], cmap='RdYlGn'), use_container_width=True)
        else:
            st.info("No drift data available")

# =================================================================
# TAB 2: ANALYTICS DEEP DIVE
# =================================================================
with tab2:
    st.header("Comprehensive Analytics Overview")
    
    # 1. KPI Metrics
    rfm_details = fetch_api("rfm-details")
    if rfm_details:
        details_df = pd.DataFrame(rfm_details)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Customers", len(details_df))
        m2.metric("Active Customers (R < 30d)", len(details_df[details_df['recency'] < 30]))
        m3.metric("Avg Monetary Value", f"${details_df['monetary'].mean():,.2f}")
        m4.metric("Max RFM Score", f"{details_df['rfm_score'].max():.2f}")
    
    st.divider()
    
    # 2. Revenue Trends
    st.subheader("💰 Revenue Trends")
    revenue_data = fetch_api("revenue-trends")
    if revenue_data:
        rev_df = pd.DataFrame(revenue_data)
        rev_df['date'] = pd.to_datetime(rev_df['date'])
        
        line_chart = alt.Chart(rev_df).mark_line(point=True).encode(
            x='date:T',
            y='revenue:Q',
            tooltip=['date:T', 'revenue:Q']
        ).interactive()
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.info("No revenue trend data available")

    st.divider()

    # 3. RFM Visualization & Details
    if rfm_details:
        col_c, col_d = st.columns([2, 1])
        
        with col_c:
            st.subheader("🔍 RFM Distribution")
            fig = px.scatter(
                details_df,
                x='recency',
                y='frequency',
                size='monetary',
                color='segment',
                hover_data=['customer_id', 'rfm_score', 'R', 'F', 'M'],
                title="Recency vs Frequency (Size = Monetary)",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_d:
            st.subheader("📊 Segment Profiles (Avg)")
            # Fix: Group only numeric columns to avoid future warning
            numeric_cols = ['recency', 'frequency', 'monetary', 'R', 'F', 'M', 'rfm_score']
            profiles = details_df.groupby('segment')[numeric_cols].mean().round(2)
            st.table(profiles)
            
        st.divider()
        
        st.subheader("📄 Customer RFM Inventory")
        # Filter interaction
        seg_list = ["All"] + list(details_df['segment'].unique())
        selected_seg = st.selectbox("Filter Inventory by Segment", seg_list)
        
        if selected_seg != "All":
            filtered_df = details_df[details_df['segment'] == selected_seg]
        else:
            filtered_df = details_df
            
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No RFM details available. Generate data and check API.")

# --- Sidebar: Explainability ---
with st.sidebar:
    st.markdown("### 🔍 Customer Inspector")
    c_id = st.text_input("Enter Customer ID")
    if c_id:
        if rfm_details:
            details_df = pd.DataFrame(rfm_details)
            cust_row = details_df[details_df['customer_id'] == c_id]
            if not cust_row.empty:
                st.success(f"Customer {c_id} Found")
                st.json(cust_row.to_dict(orient='records')[0])
            else:
                st.error("Customer Not Found")
        else:
            st.write(f"Analyzing {c_id}...")
            st.caption("(To be connected to detail endpoint in V2)")
