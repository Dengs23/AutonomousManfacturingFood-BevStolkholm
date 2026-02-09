import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Manufacturing", layout="wide")
st.title("🏭 Autonomous Manufacturing Dashboard")
st.write("Live CrewAI agents managing production")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Production", "92.5%", "+2.3%")
with col2:
    st.metric("Quality", "98.7%", "+0.5%")
with col3:
    st.metric("Uptime", "99.2%", "+0.1%")

st.success("Dashboard running successfully!")
