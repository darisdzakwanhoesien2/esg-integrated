# utils/charts.py
from typing import List, Dict, Any
import plotly.express as px
import pandas as pd

def bar_topics(topics: List[Dict[str,int]], title="Top ESG Topics"):
    """
    topics: list of {"topic": str, "mentions": int} or list of tuples
    """
    # normalize input
    if topics and isinstance(topics[0], (list, tuple)):
        df = pd.DataFrame(topics, columns=["topic","mentions"])
    elif topics and isinstance(topics[0], dict):
        df = pd.DataFrame(topics)
    else:
        df = pd.DataFrame(columns=["topic","mentions"])
    if df.empty:
        df = pd.DataFrame({"topic": [], "mentions": []})
    fig = px.bar(df.sort_values("mentions", ascending=True), x="mentions", y="topic", orientation="h", title=title)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=400)
    return fig

def sentiment_timeseries(dates: List[str], sentiments: List[float], title="Sentiment over time"):
    df = pd.DataFrame({"date": pd.to_datetime(dates), "sentiment": sentiments})
    fig = px.line(df, x="date", y="sentiment", title=title)
    fig.update_traces(mode="lines+markers")
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig

def pie_sentiment_breakdown(positive: int, neutral: int, negative: int, title="Sentiment Breakdown"):
    df = pd.DataFrame({
        "sentiment": ["positive", "neutral", "negative"],
        "count": [positive, neutral, negative]
    })
    fig = px.pie(df, names="sentiment", values="count", title=title)
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig
