import streamlit as st
from utils.data_loader import load_json

st.title("📘 ESG Framework Compliance")

reports = load_json("data/reports")
company = st.selectbox("Select report", list(reports.keys()))

report = reports[company]

st.write("### GRI Alignment")
st.json(report["framework_alignment"].get("GRI", {}))

st.write("### UNSDG Alignment")
st.json(report["framework_alignment"].get("UNSDG", {}))

st.write("### SASB Alignment")
st.json(report["framework_alignment"].get("SASB", {}))

if "LOCAL_COMPLIANCE" in report["framework_alignment"]:
    st.write("### Local ESG Compliance")
    st.json(report["framework_alignment"]["LOCAL_COMPLIANCE"])
