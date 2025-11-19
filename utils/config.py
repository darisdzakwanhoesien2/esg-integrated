APP_TITLE = "ESG Knowledge Graph Dashboard"

# DATA_DIR = "data"
# COMPANY_DIR = f"{DATA_DIR}/companies"
# REPORTS_DIR = f"{DATA_DIR}/reports"
# NEWS_DIR = f"{DATA_DIR}/news"
# SOCIAL_DIR = f"{DATA_DIR}/social_media"
# FRAMEWORKS_DIR = f"{DATA_DIR}/frameworks"
# KG_DIR = f"{DATA_DIR}/kg_exports"

# utils/config.py
from pathlib import Path

# Root data locations (adjust if needed)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
COMPANIES_DIR = DATA_DIR / "companies"
REPORTS_DIR = DATA_DIR / "reports"
NEWS_DIR = DATA_DIR / "news"
SOCIAL_DIR = DATA_DIR / "social_media"
FRAMEWORKS_DIR = DATA_DIR / "frameworks"
KG_DIR = DATA_DIR / "kg_exports"

# Default graph file
MERGED_GRAPH_JSON = KG_DIR / "merged_graph.json"

# Small helpers
def ensure_dirs():
    for d in (COMPANIES_DIR, REPORTS_DIR, NEWS_DIR, SOCIAL_DIR, FRAMEWORKS_DIR, KG_DIR):
        d.mkdir(parents=True, exist_ok=True)
