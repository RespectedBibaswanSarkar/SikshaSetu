import streamlit as st
import plotly.figure_factory as ff
import numpy as np
import pandas as pd

st.set_page_config(page_title="Class Heatmap - SikshaSetu", layout="wide")
st.title("🔥 Class Heatmap")

grade_filter = st.selectbox("Filter by Grade", ["All", "6", "7", "8"])
students = [f"STU{i:03d}" for i in range(1, 31)]
concepts = ['NUM_01', 'FRAC_01', 'ALG_01', 'ALG_02', 'GEO_01', 'MENS_01', 'RAT_01']

np.random.seed(42)
z = np.random.beta(2, 3, (30, 7))
z[:, 1] = z[:, 1] * 0.6  # Fractions lower
z[:, 2] = z[:, 2] * 0.7  # Algebra lower

fig = ff.create_annotated_heatmap(
    z=z,
    x=concepts,
    y=students,
    colorscale='RdYlGn',
    showscale=True
)
fig.update_layout(title="Student x Concept Mastery Heatmap")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🔥 Top-3 Shared Gaps")
col1, col2, col3 = st.columns(3)
col1.info("**1. FRAC_01 - Fractions Basics** (18 students < 40%)")
col2.info("**2. ALG_02 - Linear Equations** (15 students < 40%)")
col3.info("**3. ALG_01 - Intro to Algebra** (12 students < 40%)")

st.warning("**Root-cause prerequisite hint:** Fractions (FRAC_01) is a prerequisite for many topics. Focus on FRAC_01 first for maximum impact.")
