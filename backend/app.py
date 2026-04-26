import streamlit as st
import joblib
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme: dark control-room style (teal/amber accents)
st.markdown("""
    <style>
    /* Base: dark background */
    .stApp { background: linear-gradient(160deg, #0d1117 0%, #161b22 50%, #0d1117 100%); }
    
    /* Header block */
    .main-header {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%);
        border: 1px solid rgba(34, 197, 94, 0.25);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    .main-header h1 { color: #e6edf3; font-weight: 700; letter-spacing: -0.02em; margin: 0; font-size: 1.75rem; }
    .main-header p { color: #8b949e; margin: 0.35rem 0 0 0; font-size: 0.95rem; }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #e6edf3 !important; font-weight: 700; }
    
    /* Status banners */
    .stAlert [data-baseweb="notification"] {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid;
    }
    div[data-baseweb="notification"][kind="positive"] {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.08) 100%) !important;
        border-color: rgba(34, 197, 94, 0.5) !important;
        color: #86efac !important;
    }
    div[data-baseweb="notification"][kind="negative"] {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.08) 100%) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        color: #fca5a5 !important;
    }
    
    /* Chart container */
    [data-testid="stVerticalBlock"] > div:has([data-testid="stPlotlyChart"]) {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #161b22 0%, #0d1117 100%); }
    [data-testid="stSidebar"] .stMarkdown { color: #8b949e; }
    hr { border-color: #30363d !important; }
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00FFFF !important;
    }

    /* Glassmorphism Card Style */
    .glass-card {
        background: rgba(38, 39, 48, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 255, 255, 0.1);
        border: 1px solid rgba(0, 255, 255, 0.3);
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(45deg, #00FFFF, #00CCFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }

    /* Anomaly Pulse Animation */
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    
    .anomaly-box {
        background-color: rgba(255, 0, 0, 0.1);
        border: 2px solid #FF0000;
        color: #FF0000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        animation: pulse-red 2s infinite;
    }

    .normal-box {
        background-color: rgba(0, 255, 255, 0.1);
        border: 2px solid #00FFFF;
        color: #00FFFF;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-family: 'Orbitron', sans-serif;
    }
    
    .stMetric {
        background-color: transparent !important;
    }
    
    /* Plotly Chart Background */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9626/9626629.png", width=100)
    st.title("Control Panel")
    st.markdown("---")
    st.markdown("**System Status**: `ONLINE` 🟢")
    st.markdown("**AI Model**: `Isolation Forest` 🌲")
    st.markdown("**Version**: `v2.0.1` 🚀")
    
    st.markdown("---")
    confidence_threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.8)
    st.button("Reset Dashboard", type="primary")

# --- HEADER ---
st.markdown('<h1 style="text-align: center;">🛡️ AIOps: Intelligent System Monitor</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888;">Real-time Anomaly Detection coupled with <span style="color: #00FFFF">Advanced Visualization</span></p>', unsafe_allow_html=True)
st.markdown("---")

# --- INITIALIZE STATE (For Graphs) ---
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = []
if "algo_history" not in st.session_state:
    st.session_state.algo_history = []
if "timestamps" not in st.session_state:
    st.session_state.timestamps = []

def run_dashboard():
    # 1. Load the AI Brain
    try:
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        st.error("⚠️ CRITICAL ERROR: Model file not found!")
        st.warning("Please run 'train_model.py' to generate the AI brain first.")
        st.stop()

    # 2. Layout Containers
    status_container = st.empty()
    
    # Metrics Row
    st.markdown("### 📊 Live Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu_metric = st.empty()
    with col2:
        db_metric = st.empty()
    with col3:
        algo_metric = st.empty()

    # Charts Row
    st.markdown("### 📈 Performance Trends")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        cpu_chart = st.empty()
    with chart_col2:
        algo_chart = st.empty()

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
            status_container.markdown('<div class="normal-box">✅ SYSTEM HEALTHY (Normal Behavior)</div>', unsafe_allow_html=True)
        else:
            status_container.markdown('<div class="anomaly-box">🚨 CRITICAL ALERT: ANOMALY DETECTED!</div>', unsafe_allow_html=True)

        # B. Metrics with Glassmorphism
        # We can't easily wrap st.metric in custom HTML while keeping its functionality perfect, 
        # so we rely on the global CSS to style stMetric and surrounding containers if needed.
        # Here we just update the standard metrics which will look cleaner on the dark background.
        
        cpu_metric.metric("CPU Usage", f"{os_data[0]}%", delta_color="inverse")
        db_metric.metric("Active DB Threads", f"{db_conn}", "Connections")
        algo_metric.metric("Algorithm Speed", f"{algo_time:.2f} ms", "Execution Time")

        # C. Live Graphs (CPU & Algo)
        current_time = time.strftime("%H:%M:%S")
        st.session_state.cpu_history.append(os_data[0])
        st.session_state.algo_history.append(algo_time)
        st.session_state.timestamps.append(current_time)
        
        # Keep only last 50 points
        if len(st.session_state.cpu_history) > 50:
            st.session_state.cpu_history.pop(0)
            st.session_state.algo_history.pop(0)
            st.session_state.timestamps.pop(0)

        # Draw Charts using Plotly
        
        # CPU Chart
        fig_cpu = px.line(
            x=st.session_state.timestamps, 
            y=st.session_state.cpu_history,
            labels={'x': 'Time', 'y': 'CPU %'},
            template="plotly_dark"
        )
        fig_cpu.update_traces(line_color='#00FFFF', line_width=3)
        fig_cpu.update_layout(
            title="CPU Usage Over Time", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        cpu_chart.plotly_chart(fig_cpu, use_container_width=True)

        # Algo Chart
        fig_algo = px.area(
            x=st.session_state.timestamps, 
            y=st.session_state.algo_history,
            labels={'x': 'Time', 'y': 'Latency (ms)'},
            template="plotly_dark"
        )
        fig_algo.update_traces(line_color='#FF00FF', line_width=3)
        fig_algo.update_layout(
            title="Algorithm Latency", 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        algo_chart.plotly_chart(fig_algo, use_container_width=True)

        # Wait before next update
        time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    run_dashboard()