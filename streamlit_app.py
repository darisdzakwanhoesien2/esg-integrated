import streamlit as st
from utils.config import APP_TITLE

st.set_page_config(
    page_title="ESG Knowledge Graph Dashboard",
    layout="wide",
    page_icon="🌍"
)

st.title(APP_TITLE)

st.write("""
Welcome to the ESG Knowledge Graph Dashboard.

Use the sidebar to navigate between:
- Company profiles  
- Sustainability reports  
- News & social media ESG signals  
- ESG framework compliance  
- Knowledge graph relationships  
""")
