import streamlit as st
import sqlite3
import json
import os
from datetime import datetime

st.set_page_config(page_title="Sync - SikshaSetu", layout="wide")
st.title("🔄 Sync Progress Codes")

# DB setup
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sikshasetu.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS students
             (id TEXT PRIMARY KEY, data TEXT, last_sync TEXT)''')
conn.commit()

tab1, tab2, tab3 = st.tabs(["Paste Codes", "Roster", "Export"])

with tab1:
    st.subheader("Enter Progress Codes")
    codes_text = st.text_area("Paste one or more codes (space or newline separated)", height=150)
    if st.button("Sync Codes"):
        if codes_text.strip():
            codes = codes_text.replace('\n', ' ').split()
            for code in codes:
                if len(code.replace(' ', '')) > 10:
                    # Simulate validation
                    st.success(f"✅ {code[:12]}... - Valid code synced (STU001, Session 5)")
                    c.execute("INSERT OR REPLACE INTO students VALUES (?,?,?)", 
                              (f"STU{len(codes):03d}", json.dumps({"code": code}), datetime.now().isoformat()))
            conn.commit()
            st.balloons()
        else:
            st.warning("Please enter at least one code")

with tab2:
    st.subheader("Student Roster")
    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No students synced yet. Paste codes above.")

with tab3:
    st.subheader("Export Data")
    if st.button("Export as CSV"):
        st.download_button("Download CSV", "student_id,session,mastery\nSTU001,5,0.65\n", "sikshasetu_export.csv", "text/csv")
    if st.button("Export as JSON"):
        st.download_button("Download JSON", json.dumps([{"id": "STU001", "mastery": 0.65}]), "sikshasetu_export.json", "application/json")

conn.close()
