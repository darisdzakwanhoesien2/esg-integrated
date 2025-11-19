# utils/aggregations.py
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import math

def sentiment_aggregate(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)

def collect_topic_counts(sources: List[dict]) -> List[Tuple[str,int]]:
    """
    Given a list of sources (each with 'analysis' or top-level 'platforms' etc.),
    return top topic counts as list of tuples (topic, count).
    Example input: news articles where article['analysis']['esg_topics'] exists.
    """
    counter = Counter()
    for s in sources:
        # news-style
        for src in s.get("news_sources", []):
            for article in src.get("articles", []):
                for t in article.get("analysis", {}).get("esg_topics", []):
                    counter[t] += 1
        # social-style
        for platform in s.get("platforms", []):
            for post in platform.get("posts", []):
                for t in post.get("analysis", {}).get("esg_topics", []):
                    counter[t] += 1
        # reports-style
        for rpt in s.get("reports", []) if isinstance(s.get("reports", []), list) else []:
            for cat, topics in rpt.get("esg_topics", {}).items():
                for t in topics:
                    counter[t] += 1
    return counter.most_common()

def aggregate_sentiment_from_news(news_json: dict) -> Optional[float]:
    """Compute average sentiment across news json structure."""
    sentiments = []
    for src in news_json.get("news_sources", []):
        for article in src.get("articles", []):
            s = article.get("analysis", {}).get("sentiment")
            if isinstance(s, (int, float)):
                sentiments.append(s)
    return sentiment_aggregate(sentiments)

def aggregate_sentiment_from_social(social_json: dict) -> Optional[float]:
    sentiments = []
    for platform in social_json.get("platforms", []):
        for post in platform.get("posts", []):
            s = post.get("analysis", {}).get("sentiment")
            if isinstance(s, (int, float)):
                sentiments.append(s)
            for c in post.get("comments", []):
                cs = c.get("analysis", {}).get("sentiment")
                if isinstance(cs, (int, float)):
                    sentiments.append(cs)
    return sentiment_aggregate(sentiments)

def safe_ratio(a: int, b: int) -> float:
    if b == 0:
        return 0.0
    return a / b
