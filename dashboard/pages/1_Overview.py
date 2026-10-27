import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Overview - SikshaSetu", layout="wide")
st.title("📊 Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", 30)
col2.metric("Active Sessions", 24)
col3.metric("Average Mastery", "67%")
col4.metric("Questions Answered", "4,832")

st.markdown("---")
st.subheader("Class Performance Trends")

df = pd.DataFrame({
    'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    'Avg Mastery': [45, 52, 61, 67],
    'Questions': [980, 1120, 1340, 1392]
})
fig = px.line(df, x='Week', y='Avg Mastery', title='Mastery Growth')
st.plotly_chart(fig, use_container_width=True)

st.subheader("Concept-wise Performance")
concepts_df = pd.DataFrame({
    'Concept': ['Number Sense', 'Fractions', 'Algebra', 'Geometry', 'Mensuration'],
    'Mastery': [78, 45, 52, 71, 58],
    'Students Struggling': [3, 18, 15, 5, 12]
})
st.dataframe(concepts_df, use_container_width=True)
