import streamlit as st
from utils.data_loader import load_json

st.title("📊 Cross-Company Comparison")

reports = load_json("data/reports")

companies = list(reports.keys())
a = st.selectbox("Company A Report", companies)
b = st.selectbox("Company B Report", companies)

report_a = reports[a]
report_b = reports[b]

st.subheader("CO2 Emissions (Scope 1)")
st.write(f"{report_a['company']}: {report_a['metrics'].get('co2_scope1_tonnes','N/A')}")
st.write(f"{report_b['company']}: {report_b['metrics'].get('co2_scope1_tonnes','N/A')}")
