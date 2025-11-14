import streamlit as st
from utils.data_loader import load_json, load_company

st.title("🏢 Company Overview")

companies = load_json("data/companies")

company_names = {v["name"]: v for k, v in companies.items()}

selected = st.selectbox("Select company", list(company_names.keys()))
company_data = company_names[selected]

col1, col2 = st.columns(2)

with col1:
    st.subheader(company_data["name"])
    st.write(f"**Sector:** {company_data['sector']}")
    st.write(f"**Industry:** {company_data['industry']}")
    st.write(f"**Country:** {company_data['country']}")

with col2:
    st.write("### Identifiers")
    st.json(company_data["identifiers"])
