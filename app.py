"""
Decision-First UI - Streamlit App
"""
import streamlit as st
import pandas as pd
import requests
import altair as alt

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Action Center", layout="wide")

st.title("Behavior Intelligence Action Center")

# --- Helper to fetch data ---
def fetch_api(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        return r.json()
    except:
        return None

# --- Section 1: Decision Panel ---
st.header("⚠️ High Priority Actions")

actions = fetch_api("actions")

if actions:
    # Display top 3 actions as cards
    cols = st.columns(3)
    for i, action in enumerate(actions[:3]):
        with cols[i]:
            with st.container(border=True):
                st.subheader(f"{action['priority']} Priority")
                st.markdown(f"**Segment:** {action['segment']}")
                st.info(f"📢 {action['message']}")
                st.caption(f"Reason: {action['reason']}")
                
                # Feedback Buttons
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

# --- Section 2: Segment Overview ---
st.header("Segment Overview")
segments = fetch_api("segments")

if segments and "error" not in segments:
    # Convert to DF for chart
    seg_df = pd.DataFrame(list(segments.items()), columns=['Segment', 'Count'])
    
    chart = alt.Chart(seg_df).mark_bar().encode(
        x='Count',
        y=alt.Y('Segment', sort='-x'),
        color='Segment'
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No segment data available")

st.divider()

# --- Section 3: Drift Panel ---
st.header("Segment Drift (Last 24h)")
drift = fetch_api("drift")

if drift:
    drift_df = pd.DataFrame(drift)
    # Highlight big changes
    st.dataframe(drift_df.style.background_gradient(subset=['change'], cmap='RdYlGn'), use_container_width=True)
else:
    st.info("No drift data available")
    
# --- Sidebar: Explainability ---
with st.sidebar:
    st.markdown("### 🔍 Customer Inspector")
    c_id = st.text_input("Enter Customer ID")
    if c_id:
        st.write(f"Analyzing {c_id}...")
        st.caption("(To be connected to detail endpoint in V2)")
