import streamlit as st
import requests
import pandas as pd

# Configure the page
st.set_page_config(page_title="Store Intelligence Dashboard", layout="wide")
st.title("🛍️ Apex Retail: Live Store Intelligence")

# WRONG: API_URL = "http://127.0.0.1:8000"
# CORRECT:
API_URL = "https://purple-tech-challenge.onrender.com"
STORE_ID = "ST1008"

st.sidebar.header("Controls")
if st.sidebar.button("Refresh Dashboard Data"):
    st.rerun()

# --- 1. Fetch Health ---
try:
    health_res = requests.get(f"{API_URL}/health").json()
    st.sidebar.success(f"System Status: {health_res['status'].upper()}")
    st.sidebar.text(f"Events Ingested: {health_res['events_ingested']}")
except:
    st.sidebar.error("API Offline. Please run `docker compose up`.")
    st.stop()

# --- 2. Fetch Metrics ---
st.markdown("### 📊 North Star Metrics")
metrics_res = requests.get(f"{API_URL}/stores/{STORE_ID}/metrics")

if metrics_res.status_code == 200:
    data = metrics_res.json()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Unique Visitors", data["unique_visitors_today"])
    col2.metric("Converted Visitors", data["converted_visitors"])
    col3.metric("Conversion Rate", f"{data['conversion_rate_percentage']}%")
else:
    st.warning("No event data found for this store. Please ingest data first.")

st.divider()

# --- 3. Anomalies & Alerts ---
st.markdown("### 🚨 Operational Anomalies")
anomalies_res = requests.get(f"{API_URL}/stores/{STORE_ID}/anomalies")

if anomalies_res.status_code == 200:
    anomalies = anomalies_res.json().get("active_anomalies", [])
    if not anomalies:
        st.success("All systems nominal. No active anomalies.")
    else:
        for alert in anomalies:
            if alert["severity"] == "CRITICAL":
                st.error(f"**{alert['type']}**: {alert['description']} ➔ *{alert['suggested_action']}*")
            else:
                st.warning(f"**{alert['type']}**: {alert['description']} ➔ *{alert['suggested_action']}*")

st.divider()

# --- 4. Conversion Funnel ---
st.markdown("### 📉 Real-Time Conversion Funnel")
funnel_res = requests.get(f"{API_URL}/stores/{STORE_ID}/funnel")

if funnel_res.status_code == 200:
    funnel_data = funnel_res.json().get("funnel", {})
    
    # Format data for a bar chart
    stages = []
    counts = []
    for stage, info in funnel_data.items():
        # Clean up the stage name (e.g., "1_entries" -> "Entries")
        clean_name = stage.split("_", 1)[1].replace("_", " ").title()
        stages.append(clean_name)
        counts.append(info["count"])
        
    df = pd.DataFrame({"Stage": stages, "Customers": counts})
    st.bar_chart(df.set_index("Stage"))