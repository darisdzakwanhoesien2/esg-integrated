import streamlit as st
import os
import json
import re
from utils.data_loader import load_json

st.set_page_config(page_title="ESG Dashboard", layout="wide", page_icon="🌍")

# ============================================================
# 🔍 UNIVERSAL FILENAME NORMALIZATION
# ============================================================

def normalize(s):
    """Normalize a string to match across company names, IDs, filenames."""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def detect_files_for_company(company_name, company_id):
    """
    Auto-detect company files by matching either:
    - company name (cleaned)
    - company ID (cleaned)
    - partial fragments of either
    """
    name_key = normalize(company_name)
    id_key = normalize(company_id)

    def match_file(fname):
        f = normalize(fname)
        return (name_key in f) or (id_key in f)

    # news
    news_files = [f for f in os.listdir("data/news") if match_file(f)]
    # reports
    report_files = [f for f in os.listdir("data/reports") if match_file(f)]
    # social media
    social_files = [f for f in os.listdir("data/social_media") if match_file(f)]

    return {
        "news": [f"data/news/{f}" for f in news_files],
        "reports": [f"data/reports/{f}" for f in report_files],
        "social": [f"data/social_media/{f}" for f in social_files]
    }


def load_json_file(path):
    """Safely load JSON; returns None if fails."""
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

# ============================================================
# LOAD ALL CORE DATA
# ============================================================

companies = load_json("data/companies")

# Map company name to its JSON file
company_list = {data["name"]: file for file, data in companies.items()}

# ============================================================
# SELECT COMPANY
# ============================================================

st.title("🌍 Company ESG Dashboard")

selected_company = st.selectbox("Select a Company", list(company_list.keys()))
company_file = company_list[selected_company]

company = companies[company_file]
company_name = company["name"]
company_id = company["company_id"]

# ============================================================
# AUTO-DETECT report, news, social files
# ============================================================

detected = detect_files_for_company(company_name, company_id)

report_files = detected["reports"]
news_files = detected["news"]
social_files = detected["social"]

# Load them all
reports = [load_json_file(p) for p in report_files]
news_data = [load_json_file(p) for p in news_files]
social_data = [load_json_file(p) for p in social_files]

# Filter out None
reports = [r for r in reports if r]
news_data = [n for n in news_data if n]
social_data = [s for s in social_data if s]

# ============================================================
# SECTION 1 — COMPANY OVERVIEW
# ============================================================

st.header("🏢 Company Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader(company["name"])
    st.write(f"**Sector:** {company['sector']}")
    st.write(f"**Industry:** {company['industry']}")
    st.write(f"**Country:** {company['country']}")

with col2:
    st.subheader("Identifiers")
    st.json(company["identifiers"])

st.markdown("---")

# ============================================================
# SECTION 2 — SUSTAINABILITY REPORTS
# ============================================================

st.header("📄 Sustainability Reports")

if reports:
    for r in reports:
        st.subheader(f"Report Year: {r.get('year', 'Unknown')}")
        st.write(r.get("overall_summary", ""))

        c1, c2 = st.columns(2)
        with c1:
            st.write("### Key Metrics")
            st.json(r.get("metrics", {}))
        with c2:
            st.write("### ESG Topics")
            st.json(r.get("esg_topics", {}))

        st.write("### Claims")
        st.json(r.get("claims", []))

        st.write("### Framework Alignment")
        st.json(r.get("framework_alignment", {}))

else:
    st.warning("No report files found for this company.")

st.markdown("---")

# ============================================================
# SECTION 3 — NEWS
# ============================================================

st.header("📰 News ESG Analytics")

if news_data:
    for nf in news_data:
        st.subheader(f"News File: {nf.get('year', 'Unknown Year')}")

        for source in nf.get("news_sources", []):
            with st.expander(f"{source['source_name']} ({source['source_type']})"):
                for article in source.get("articles", []):
                    st.write(f"### {article['title']}")
                    st.caption(article.get("published_date", ""))
                    st.write(article.get("content_cleaned", ""))
                    st.json(article.get("analysis", {}))

        st.write("### Aggregated News Analysis")
        st.json(nf.get("aggregated_analysis", {}))
else:
    st.warning("No news files found for this company.")

st.markdown("---")

# ============================================================
# SECTION 4 — SOCIAL MEDIA
# ============================================================

st.header("💬 Social Media Insights")

if social_data:
    for sm in social_data:
        st.subheader(f"Dataset: {sm.get('year', 'Unknown Year')}")
        for platform in sm.get("platforms", []):
            st.write(f"## {platform['platform']}")
            for post in platform.get("posts", []):
                with st.expander(f"Post ID: {post['post_id']}"):
                    st.write(post.get("content_raw", ""))
                    st.json(post.get("analysis", {}))
                    if "comments" in post:
                        st.write("### Comments")
                        st.json(post["comments"])

        st.write("### Aggregated Social Media Analysis")
        st.json(sm.get("aggregated_analysis", {}))
else:
    st.warning("No social media datasets found for this company.")

st.markdown("---")

# ============================================================
# SECTION 5 — KNOWLEDGE GRAPH (optional)
# ============================================================

st.header("🕸 Knowledge Graph")
st.info("Graph viewer module can be integrated here (PyVis/NetworkX).")
