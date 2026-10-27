import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Student View - SikshaSetu", layout="wide")
st.title("👤 Student View")

student = st.selectbox("Select Student", [f"STU{i:03d}" for i in range(1, 31)])
st.markdown(f"### {student}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Mastery Overview")
    concepts = ['NUM_01', 'FRAC_01', 'ALG_01', 'ALG_02', 'GEO_01']
    mastery = [0.78, 0.32, 0.45, 0.28, 0.65]
    for c, m in zip(concepts, mastery):
        st.write(f"{c}: {m*100:.0f}%")
        st.progress(m)

with col2:
    st.subheader("Mastery Radar")
    categories = concepts + [concepts[0]]
    values = mastery + [mastery[0]]
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Trend Over Sessions")
sessions = [1,2,3,4,5]
trend = [0.35, 0.42, 0.48, 0.55, 0.62]
fig = go.Figure()
fig.add_trace(go.Scatter(x=sessions, y=trend, mode='lines+markers', name='Avg Mastery'))
fig.update_layout(xaxis_title="Session", yaxis_title="Mastery")
st.plotly_chart(fig, use_container_width=True)

st.subheader("RL Action Log")
st.dataframe({
    'Session': [5,5,5,4,4],
    'Action': ['(ALG_02, 2)', '(FRAC_01, 1)', '(ALG_02, 2)', '(FRAC_01, 1)', '(NUM_01, 1)'],
    'Reason': ['Frontier - prereq met', 'Review forgotten', 'ZPD zone', 'Frontier', 'Maintenance'],
    'Result': ['Correct', 'Wrong', 'Correct', 'Correct', 'Correct']
}, use_container_width=True)

st.subheader("Suggested Next Steps")
st.success("1. Focus on FRAC_01 (Fractions) - foundational for algebra")
st.info("2. Practice ALG_02 with more scaffolds")
st.warning("3. Review ALG_01 concepts before advancing")
