import streamlit as st
import os

st.set_page_config(page_title="Pack Generator - SikshaSetu", layout="wide")
st.title("📦 Pack Generator")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Options")
    pack_type = st.radio("Pack Type", ["Generic", "Student-Specific"])
    if pack_type == "Student-Specific":
        student = st.selectbox("Student", [f"STU{i:03d}" for i in range(1, 31)])
    language = st.selectbox("Language", ["English", "Hindi", "Both"])
    grade = st.multiselect("Grades", ["6", "7", "8"], default=["6","7","8"])
    concepts = st.multiselect("Concepts", ["All"] + [f"NUM_{i:02d}" for i in range(1,7)], default=["All"])

with col2:
    st.subheader("Preview")
    st.info("**Target:** <= 250 KB | Works offline | file:// compatible")
    st.write("Features:")
    st.write("- Diagnostic test")
    st.write("- RL-driven practice")
    st.write("- Progress code generation")
    st.write("- QR code")
    st.write("- EN/HI toggle")
    st.write("- Light/Dark mode")
    st.write("- Offline badge")

if st.button("🔨 Build Pack"):
    with st.spinner("Building..."):
        os.system("cd .. && python packgen/build_pack.py 2>&1")
    st.success("Pack built successfully!")
    
pack_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'packgen', 'sikshasetu_pack.html')
if os.path.exists(pack_path):
    size = os.path.getsize(pack_path) / 1024
    st.metric("File Size", f"{size:.1f} KB")
    with open(pack_path, 'r', encoding='utf-8') as f:
        html = f.read()
    st.download_button("📥 Download HTML Pack", html, "sikshasetu_pack.html", "text/html")
else:
    st.warning("Pack not built yet. Click 'Build Pack' above.")
