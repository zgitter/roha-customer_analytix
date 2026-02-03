"""
Multi-Tab Dashboard - Action Center & Analytics Deep Dive
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import config
import api  # DIRECT IMPORT

# API_URL - No longer needed for logic, but maybe for reference if needed
# API_URL = config.dashboard.api_url

st.set_page_config(page_title=config.app.name, layout="wide")

# Set dynamic Plotly template
PLOTLY_TEMPLATE = "plotly_dark" if config.dashboard.theme.lower() == "dark" else "plotly_white"

# Initialize session state for inspector
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = None

# --- Helper to fetch data (Refactored for Direct Import) ---
@st.cache_data(ttl=60)
def fetch_data(endpoint):
    """
    Directly calls API functions instead of HTTP requests.
    This simulates the API layer within the Streamlit process.
    """
    try:
        if endpoint == "actions":
            return api.get_actions()
        elif endpoint == "segments":
            return api.get_segments()
        elif endpoint == "drift":
            return api.get_drift()
        elif endpoint == "rfm-details":
            return api.get_rfm_details()
        elif endpoint == "revenue-trends":
            return api.get_revenue_trends()
        return None
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return None

# --- Main Layout ---
st.title("Behavior Intelligence Platform")

tab1, tab2, tab3 = st.tabs(["🎯 Action Center", "📊 KPI Dashboard", "📈 Analytics Deep Dive"])

# =================================================================
# TAB 1: ACTION CENTER
# =================================================================
with tab1:
    st.subheader("🏁 Priority Activity Board")
    
    actions_raw = fetch_data("actions")
    
    if actions_raw is None:
        st.error("API Offline or No Data")
    elif len(actions_raw) == 0:
        st.info("No pending actions.")
    else:
        actions_df = pd.DataFrame(actions_raw)
        
        # 3 Column Layout
        cols = st.columns(3)
        priorities = ["High", "Medium", "Low"]
        
        for idx, priority in enumerate(priorities):
            with cols[idx]:
                st.info(f"**{priority} Priority**")
                
                # Filter for this priority column
                priority_subset = actions_df[actions_df['priority'] == priority]
                
                if priority_subset.empty:
                    st.caption("No pending actions.")
                else:
                    # Group by Campaign
                    campaigns = priority_subset.groupby(['action_id', 'message', 'segment', 'reason']).size().reset_index(name='count')
                    
                    for _, camp in campaigns.iterrows():
                        # Create a Card-like container
                        with st.container(border=True):
                            st.markdown(f"**{camp['message']}**")
                            st.caption(f"🎯 {camp['segment']} • {camp['count']} users")
                            
                            # Filter customers for this specific campaign card
                            camp_customers = priority_subset[
                                (priority_subset['action_id'] == camp['action_id']) & 
                                (priority_subset['segment'] == camp['segment'])
                            ]
                            
                            # Compact Data Editor
                            # Just show ID and Score + Select
                            df_display = camp_customers[['customer_id', 'score']].copy()
                            df_display['Select'] = False
                            
                            edited_df = st.data_editor(
                                df_display,
                                column_config={
                                    "Select": st.column_config.CheckboxColumn("", width="small", default=False),
                                    "customer_id": st.column_config.TextColumn("ID", width="small", disabled=True),
                                    "score": st.column_config.NumberColumn("RFM", width="small", format="%.2f", disabled=True)
                                },
                                hide_index=True,
                                key=f"grid_{camp['action_id']}_{camp['segment']}",
                                use_container_width=True,
                                height=200 # Scrollable fixed height
                            )
                            
                            # Actions Row
                            b_col1, b_col2 = st.columns(2)
                            selected_rows = edited_df[edited_df['Select']]
                            
                            if b_col1.button("✅ Apply", key=f"btn_apply_{camp['action_id']}_{camp['segment']}", use_container_width=True):
                                if not selected_rows.empty:
                                    # Construct FeedbackItem objects
                                    items = [
                                        api.FeedbackItem(
                                            action_id=camp['action_id'], 
                                            segment=camp['segment'], 
                                            applied="yes"
                                        )
                                        for _, row in selected_rows.iterrows()
                                    ]
                                    
                                    # Call API directly
                                    api.save_batch_feedback(api.BatchFeedbackItem(items=items))
                                    
                                    st.toast(f"Applied {len(selected_rows)} actions")
                                    st.rerun()
                                else:
                                    st.warning("Select users first")

                            if b_col2.button("❌ Ignore", key=f"btn_ignore_{camp['action_id']}_{camp['segment']}", use_container_width=True):
                                if not selected_rows.empty:
                                    items = [
                                        api.FeedbackItem(
                                            action_id=camp['action_id'], 
                                            segment=camp['segment'], 
                                            applied="no"
                                        )
                                        for _, row in selected_rows.iterrows()
                                    ]
                                    
                                    api.save_batch_feedback(api.BatchFeedbackItem(items=items))
                                    
                                    st.toast(f"Ignored {len(selected_rows)} actions")
                                    st.rerun()
                                else:
                                    st.warning("Select users first")
                                    
                            # Quick Inspect Link (using selectbox for space efficiency)
                            cust_list = [""] + list(camp_customers['customer_id'])
                            inspect_id = st.selectbox(
                                "Inspect:", 
                                cust_list, 
                                key=f"insp_{camp['action_id']}_{camp['segment']}",
                                label_visibility="collapsed",
                                placeholder="Select to Inspect..."
                            )
                            if inspect_id:
                                st.session_state.selected_customer = inspect_id
                                
    st.divider()
    
    # Intelligence Section (Moved below decisions)
    st.subheader("📊 Intelligence Overview")
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown("**Segment Distribution**")
        segments = fetch_data("segments")
        if segments and "error" not in segments:
            seg_df = pd.DataFrame(list(segments.items()), columns=['Segment', 'Count'])
            chart = alt.Chart(seg_df).mark_bar().encode(
                x='Count',
                y=alt.Y('Segment', sort='-x'),
                color='Segment',
                tooltip=['Segment', 'Count']
            )
            st.altair_chart(chart, use_container_width=True)
            
    with col_b:
        st.markdown("**Stability Monitor (Drift)**")
        drift = fetch_data("drift")
        if drift:
            drift_df = pd.DataFrame(drift)
            st.dataframe(
                drift_df[['segment_name', 'change', 'current_percentage']].style.background_gradient(subset=['change'], cmap='RdYlGn'), 
                use_container_width=True
            )


# =================================================================
# TAB 2: KPI DASHBOARD
# =================================================================
with tab2:
    st.header("🔑 Key Performance Indicators")
    
    rfm_details = fetch_data("rfm-details")
    revenue_data = fetch_data("revenue-trends")
    
    if rfm_details:
        details_df = pd.DataFrame(rfm_details)
        
        # Row 1: Big Metrics
        k1, k2, k3, k4 = st.columns(4)
        
        total_customers = len(details_df)
        active_customers = len(details_df[details_df['recency'] < 30])
        total_revenue = details_df['monetary'].sum()
        avg_score = details_df['rfm_score'].mean()
        
        k1.metric("Total Customers", f"{total_customers:,}")
        k2.metric("Active Users (30d)", f"{active_customers:,}", delta=f"{active_customers/total_customers:.1%} of base")
        k3.metric("Total Revenue", f"{config.CURRENCY_SYMBOL} {total_revenue:,.0f}")
        k4.metric("Avg Health Score", f"{avg_score:.2f}/5.0")
        
        st.divider()
        
        # Row 2: Charts
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("💰 Revenue Growth")
            if revenue_data:
                rev_df = pd.DataFrame(revenue_data)
                rev_df['date'] = pd.to_datetime(rev_df['date'])
                
                chart_rev = alt.Chart(rev_df).mark_area(
                    line={'color':'#29b5e8'},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='#29b5e8', offset=0),
                               alt.GradientStop(color='rgba(41, 181, 232, 0)', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x='date:T',
                    y='revenue:Q',
                    tooltip=['date:T', 'revenue:Q']
                ).properties(height=350)
                st.altair_chart(chart_rev, use_container_width=True)
            else:
                st.info("No revenue data.")
                
        with c2:
            st.subheader("👥 User Segments")
            # Donut Chart
            seg_counts = details_df['segment'].value_counts().reset_index()
            seg_counts.columns = ['segment', 'count']
            
            fig_donut = px.pie(
                seg_counts, 
                names='segment', 
                values='count', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe, # Use more compatible palette
                template=PLOTLY_TEMPLATE
            )
            fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=350)
            st.plotly_chart(fig_donut, use_container_width=True)

    else:
        st.warning("No data available.")

# =================================================================
# TAB 3: ANALYTICS DEEP DIVE
# =================================================================
with tab3:
    st.header("📈 Data Explorer")
    
    # Re-fetch or reuse
    # fetch_data is cached so this is fine
    rfm_details = fetch_data("rfm-details")
    
    if rfm_details:
        details_df = pd.DataFrame(rfm_details)
        
        # Scatter Plot moved here
        st.subheader("🔍 Segmentation Matrix")
        fig = px.scatter(
            details_df,
            x='recency',
            y='frequency',
            size='monetary',
            color='segment',
            hover_data=['customer_id', 'rfm_score', 'R', 'F', 'M'],
            title="Recency vs Frequency (Bubble Size = Monetary)",
            template=PLOTLY_TEMPLATE,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # Profiles
        st.subheader("📊 Segment Profiles")
        numeric_cols = ['recency', 'frequency', 'monetary', 'R', 'F', 'M', 'rfm_score']
        profiles = details_df.groupby('segment')[numeric_cols].mean().round(2)
        st.dataframe(profiles, use_container_width=True)
            
        st.divider()
        
        # Inventory
        st.subheader("📋 Customer Inventory")
        seg_list = ["All"] + list(details_df['segment'].unique())
        selected_seg = st.selectbox("Filter by Segment", seg_list, key="inv_seg_filter")
        
        if selected_seg != "All":
            filtered_df = details_df[details_df['segment'] == selected_seg]
        else:
            filtered_df = details_df
            
        st.dataframe(filtered_df, use_container_width=True)

# =================================================================
# SIDEBAR: BEAUTIFIED INSPECTOR
# =================================================================
with st.sidebar:
    st.header("🔍 Customer Profile")
    
    # Manual Search
    search_id = st.text_input("Search Customer ID")
    if search_id:
        st.session_state.selected_customer = search_id
        
    # Logic to display profile
    if st.session_state.selected_customer:
        c_id = st.session_state.selected_customer
        
        # Need RFM details to show profile
        # Ideally this is a separate API call per customer for scale, but here we reuse the bulk fetch or cached list
        rfm_details = fetch_data("rfm-details")
        rfm_details_df = pd.DataFrame(rfm_details or [])
             
        if not rfm_details_df.empty:
             cust_row = rfm_details_df[rfm_details_df['customer_id'] == c_id]
             
             if not cust_row.empty:
                 data = cust_row.iloc[0]
                 
                 # Styled Profile Card
                 st.markdown(f"### 👤 {data['customer_id']}")
                 st.markdown(f"**Segment:** `{data['segment']}`")
                 
                 st.divider()
                 
                 k1, k2, k3 = st.columns(3)
                 k1.metric("Recency", f"{data['recency']}d", help="Days since last purchase")
                 k2.metric("Frequency", f"{data['frequency']}x", help="Total Transactions")
                 k3.metric("Monetary", f"{config.CURRENCY_SYMBOL} {data['monetary']:,.0f}", help="Total Spend")
                 
                 st.progress(data['R']/5, text=f"Recency Score: {data['R']}/5")
                 st.progress(data['F']/5, text=f"Frequency Score: {data['F']}/5")
                 st.progress(data['M']/5, text=f"Monetary Score: {data['M']}/5")
                 
                 st.metric("Composite RFM Score", f"{data['rfm_score']}/5.0")
                 
             else:
                 st.warning(f"Customer {c_id} not found locally.")
        else:
             st.info("Loading customer data...")
    else:
        st.info("Select a customer from the Action Center or search above to view profile.")
