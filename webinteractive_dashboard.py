# web_dashboard.py - Interactive Web Dashboard
import time
import json
import random
from datetime import datetime
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# Setup CrewAI
try:
    from crewai import Agent, Task, Crew, Process
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "crewai"])
    from crewai import Agent, Task, Crew, Process

# Initialize Streamlit
st.set_page_config(
    page_title="Autonomous Manufacturing Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .alert-card {
        background: #fff3cd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

class ManufacturingDashboard:
    def __init__(self):
        if 'agents' not in st.session_state:
            st.session_state.agents = {}
            st.session_state.cycle_count = 0
            st.session_state.history = []
            st.session_state.sensors = self._generate_sensor_data()
            st.session_state.alerts = []
    
    def _generate_sensor_data(self):
        sensors = {}
        sensor_names = [
            "temperature_c", "pressure_bar", "ph_level", "flow_rate_lph",
            "vibration_x", "vibration_y", "vibration_z", "ultrasound_leak_db",
            "acoustic_emission", "orp_redox_mv", "humidity_rh",
            "vision_defect_score", "vision_contaminant_score", "co2_ppm",
            "o2_percent", "voc_ppm", "differential_pressure_bar"
        ]
        
        for sensor in sensor_names:
            if "vibration" in sensor:
                sensors[sensor] = round(random.uniform(0.1, 0.8), 3)
            elif "temperature" in sensor:
                sensors[sensor] = round(random.uniform(22.0, 28.0), 1)
            elif "pressure" in sensor:
                sensors[sensor] = round(random.uniform(0.9, 1.1), 2)
            elif "vision" in sensor:
                sensors[sensor] = round(random.uniform(0.0, 0.3), 3)
            else:
                sensors[sensor] = round(random.uniform(0, 100), 2)
        return sensors
    
    def run_cycle(self):
        st.session_state.cycle_count += 1
        st.session_state.sensors = self._generate_sensor_data()
        
        # Detect alerts
        alerts = []
        for sensor, value in st.session_state.sensors.items():
            if "vibration" in sensor and value > 0.7:
                alerts.append(f"High vibration: {sensor} = {value:.3f}")
            elif "temperature" in sensor and value > 27.0:
                alerts.append(f"High temperature: {sensor} = {value:.1f}°C")
        
        cycle_data = {
            "cycle": st.session_state.cycle_count,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "alerts": alerts,
            "sensor_count": len(alerts),
            "status": "ALERT" if alerts else "NORMAL"
        }
        
        st.session_state.history.append(cycle_data)
        st.session_state.alerts = alerts
        
        return cycle_data

# Initialize dashboard
dashboard = ManufacturingDashboard()

# Main Dashboard UI
st.markdown('<div class="main-header">🏭 Autonomous Manufacturing Dashboard</div>', unsafe_allow_html=True)
st.markdown("**Food & Beverage System - Stockholm Region**")

# Sidebar Controls
with st.sidebar:
    st.title("Control Panel")
    
    if st.button("🔄 Run Single Cycle", use_container_width=True):
        cycle_data = dashboard.run_cycle()
        st.success(f"Cycle #{cycle_data['cycle']} completed!")
    
    st.subheader("System Status")
    st.metric("Total Cycles", st.session_state.cycle_count)
    st.metric("Active Alerts", len(st.session_state.alerts))
    
    st.subheader("Settings")
    auto_run = st.toggle("Auto-run Simulation", value=False)
    if auto_run:
        interval = st.slider("Update interval (seconds)", 2, 30, 10)
    
    if st.button("Reset System", type="secondary"):
        st.session_state.agents = {}
        st.session_state.cycle_count = 0
        st.session_state.history = []
        st.session_state.sensors = dashboard._generate_sensor_data()
        st.session_state.alerts = []
        st.rerun()

# Main Content Area
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🚨 Alert Status")
    if st.session_state.alerts:
        for alert in st.session_state.alerts:
            st.markdown(f'<div class="alert-card">⚠️ {alert}</div>', unsafe_allow_html=True)
    else:
        st.success("✅ All systems normal")
    
    st.subheader("🤖 Agents")
    agents = [
        {"name": "Alert Agent", "status": "🟢 Active", "last_run": "Now"},
        {"name": "Analyzer Agent", "status": "🟢 Active", "last_run": "Now"},
        {"name": "Production Agent", "status": "🟢 Active", "last_run": "Now"},
        {"name": "Optimum Agent", "status": "🟢 Active", "last_run": "Now"},
    ]
    
    for agent in agents:
        st.markdown(f'<div class="agent-card"><b>{agent["name"]}</b><br>{agent["status"]} | Last run: {agent["last_run"]}</div>', unsafe_allow_html=True)

with col2:
    st.subheader("📡 Sensor Data")
    
    # Display critical sensors
    critical_sensors = ["temperature_c", "pressure_bar", "vibration_x", "vibration_y", "vibration_z"]
    for sensor in critical_sensors:
        value = st.session_state.sensors.get(sensor, 0)
        
        # Create gauge indicators
        col_a, col_b = st.columns([1, 3])
        with col_a:
            if "vibration" in sensor:
                color = "🔴" if value > 0.7 else "🟢"
            elif "temperature" in sensor:
                color = "🟡" if value > 27.0 else "🟢"
            else:
                color = "🔵"
            st.write(color)
        with col_b:
            st.progress(value/1.0 if "vibration" in sensor else value/30.0)
            st.caption(f"{sensor}: {value:.3f}")
    
    # Sensor values table
    sensor_df = pd.DataFrame(list(st.session_state.sensors.items()), columns=['Sensor', 'Value'])
    st.dataframe(sensor_df.head(8), use_container_width=True)

with col3:
    st.subheader("📊 Analytics")
    
    if st.session_state.history:
        # Create history chart
        history_df = pd.DataFrame(st.session_state.history)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=history_df['cycle'],
            y=history_df['sensor_count'],
            mode='lines+markers',
            name='Alerts per Cycle',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Alert History",
            xaxis_title="Cycle Number",
            yaxis_title="Number of Alerts",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # System metrics
    st.metric("System Uptime", "99.7%", "+0.3%")
    st.metric("Production Efficiency", "96.2%", "+1.8%")
    st.metric("Quality Score", "98.1%", "+0.9%")

# Bottom section
st.markdown("---")
st.subheader("Cycle History")
if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)
    st.dataframe(history_df, use_container_width=True)
else:
    st.info("No cycles run yet. Click 'Run Single Cycle' to start.")

# Auto-run logic
if 'auto_run' in locals() and auto_run:
    time.sleep(interval)
    dashboard.run_cycle()
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Autonomous Manufacturing System v2.0 | 4 AI Agents | 17 Sensors | Stockholm Food & Beverage*")
