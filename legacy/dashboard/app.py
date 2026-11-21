import streamlit as st
import json
import os

st.set_page_config(
    page_title="SikshaSetu v2 - Teacher Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 1rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("🎓 SikshaSetu v2 - Teacher Dashboard")
st.caption("Offline-first Adaptive Learning System for Class 6-8 Maths | North-East India")

# Load data
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
try:
    with open(os.path.join(data_dir, 'concepts.json'), 'r', encoding='utf-8') as f:
        concepts = json.load(f)
    st.success(f"Loaded {len(concepts)} concepts")
except:
    st.error("Concepts not found")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Students", "30", "+5")
col2.metric("Sessions", "156", "+12")
col3.metric("Class Mean Mastery", "64%", "+8%")
col4.metric("Top Gaps", "Fractions, Algebra", "")

st.markdown("---")
st.info("Navigate using the sidebar pages: Overview, Class Heatmap, Student View, Sync, Pack Generator, RL Lab, Evaluation, Skill Pathway, Demo Mode")
