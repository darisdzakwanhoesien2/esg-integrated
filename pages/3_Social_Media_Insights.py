import streamlit as st
from utils.data_loader import load_json

st.title("💬 Social Media Insights")

data = load_json("data/social_media")

report = st.selectbox("Select dataset", list(data.keys()))
social = data[report]

st.write("### Sentiment Summary")
st.json(social["aggregated_analysis"]["platform_sentiments"])

st.write("### Top ESG Topics")
st.json(social["aggregated_analysis"]["top_esg_topics"])

st.write("### Raw Posts By Platform")
for platform in social["platforms"]:
    st.write(f"## {platform['platform']}")
    st.json(platform["posts"])
