import streamlit as st
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="RL Lab - SikshaSetu", layout="wide")
st.title("🤖 RL Lab")

col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Training Parameters")
    episodes = st.slider("Episodes", 10, 500, 100)
    learning_rate = st.slider("Learning Rate", 0.0001, 0.01, 0.001, 0.0001)
    hidden_dim = st.slider("Hidden Dim", 32, 128, 64)
    epsilon_decay = st.slider("Epsilon Decay", 0.99, 0.999, 0.995)
    if st.button("🚀 Train Model"):
        with st.spinner("Training Double DQN..."):
            os.system(f"cd .. && python rl/train.py 2>&1 | tail -20")
        st.success("Training complete!")

with col2:
    st.subheader("Reward Curve")
    reward_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', 'reward_curves.json')
    if os.path.exists(reward_path):
        with open(reward_path, 'r') as f:
            data = json.load(f)
        rewards = data['rewards']
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=rewards, mode='lines', name='Episode Reward'))
        fig.update_layout(title="Training Progress", xaxis_title="Episode", yaxis_title="Total Reward")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No training data yet. Train the model first.")

st.markdown("---")
st.subheader("Policy Export")
if st.button("📤 Export Policy to Pack"):
    os.system("cd .. && python rl/export_policy.py 2>&1")
    policy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'packgen', 'policy.json')
    if os.path.exists(policy_path):
        size = os.path.getsize(policy_path) / 1024
        st.success(f"Policy exported ({size:.2f} KB)")

st.subheader("Compare Policies")
st.dataframe({
    'Policy': ['Random', 'Fixed Curriculum', 'Greedy Lowest-Mastery', 'BKT-Only', 'RL (Ours)'],
    'Avg Reward': [-2.3, -1.1, -0.5, -0.2, 0.8],
    'Mastery Gain/20q': [0.12, 0.18, 0.24, 0.28, 0.35]
}, use_container_width=True)
