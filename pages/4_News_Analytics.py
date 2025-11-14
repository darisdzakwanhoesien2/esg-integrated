import streamlit as st
from utils.data_loader import load_json

st.title("📰 News ESG Analytics")

news = load_json("data/news")

selected = st.selectbox("Select a company news file", list(news.keys()))
news_file = news[selected]

for source in news_file["news_sources"]:
    st.header(source["source_name"])
    for article in source["articles"]:
        st.subheader(article["title"])
        st.write(article["published_date"])
        st.write(article["content_cleaned"])
        st.json(article["analysis"])
