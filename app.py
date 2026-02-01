import streamlit as st
import joblib
import time
import pandas as pd
import plotly.express as px  # For nice graphs
import os_monitor
import db_monitor
import algo_monitor

# --- CONFIGURATION ---
MODEL_FILE = "health_model.pkl"
REFRESH_RATE = 1  # How often to update the dashboard (seconds)

# --- PAGE SETUP ---
st.set_page_config(
    page_title="AI System Monitor",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS to make the "Alert" banner really pop
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ AIOps: Intelligent System Health Monitor")
st.markdown("Real-time Anomaly Detection using **Isolation Forest**")
st.markdown("---")

# --- INITIALIZE STATE (For Graphs) ---
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = []
if "algo_history" not in st.session_state:
    st.session_state.algo_history = []

def run_dashboard():
    # 1. Load the AI Brain
    try:
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        st.error("⚠️ CRITICAL ERROR: Model file not found!")
        st.warning("Please run 'train_model.py' to generate the AI brain first.")
        st.stop()

    # 2. Layout Containers
    # We use st.empty() so we can overwrite these sections every second
    status_container = st.empty()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        cpu_metric = st.empty()
    with col2:
        db_metric = st.empty()
    with col3:
        algo_metric = st.empty()

    chart_container = st.empty()

    # 3. Main Monitoring Loop
    while True:
        # --- GET LIVE DATA ---
        os_data = os_monitor.get_os_metrics() # [CPU, RAM, Disk]
        db_conn = db_monitor.get_db_metrics() # [Active Threads]
        algo_time = algo_monitor.run_dummy_algorithm() # [ms]

        # Prepare data for AI (Must be 2D list: [[col1, col2...]])
        # Order: CPU, RAM, Disk, DB, Algo
        input_data = [[os_data[0], os_data[1], os_data[2], db_conn, algo_time]]

        # --- AI PREDICTION ---
        # 1 = Normal, -1 = Anomaly
        prediction = model.predict(input_data)[0]

        # --- UPDATE UI ---
        
        # A. Status Banner
        if prediction == 1:
            status_container.success("✅ SYSTEM HEALTHY (Normal Behavior)")
        else:
            status_container.error("🚨 CRITICAL ALERT: ANOMALY DETECTED!")

        # B. Metrics
        cpu_metric.metric("CPU Usage", f"{os_data[0]}%", delta_color="inverse")
        db_metric.metric("Active DB Threads", f"{db_conn}", "Connections")
        algo_metric.metric("Algorithm Speed", f"{algo_time:.2f} ms", "Execution Time")

        # C. Live Graphs (CPU & Algo)
        st.session_state.cpu_history.append(os_data[0])
        st.session_state.algo_history.append(algo_time)
        
        # Keep only last 50 points to keep graph clean
        if len(st.session_state.cpu_history) > 50:
            st.session_state.cpu_history.pop(0)
            st.session_state.algo_history.pop(0)

        # Draw Chart
        with chart_container:
            chart_data = pd.DataFrame({
                "CPU (%)": st.session_state.cpu_history,
                "Algo Time (ms)": st.session_state.algo_history
            })
            st.line_chart(chart_data)

        # Wait before next update
        time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    run_dashboard()