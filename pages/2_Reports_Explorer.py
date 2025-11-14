import streamlit as st
from utils.data_loader import load_json

st.title("📄 Sustainability Reports Explorer")

reports = load_json("data/reports")

selected_report = st.selectbox("Choose report", list(reports.keys()))
report = reports[selected_report]

st.subheader(report["company"] + " — " + str(report["year"]))
st.write(report["overall_summary"])

st.write("### Metrics")
st.json(report["metrics"])

st.write("### ESG Topics")
st.json(report["esg_topics"])

st.write("### Claims Made in Report")
st.json(report["claims"])
