# import json
# import os

def load_json(folder_path):
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r") as f:
                data[filename] = json.load(f)
    return data

def load_company(company_id):
    path = f"data/companies/{company_id}.json"
    with open(path) as f: return json.load(f)

# utils/data_loader.py
import json
import os
import re
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional

from .config import COMPANIES_DIR, REPORTS_DIR, NEWS_DIR, SOCIAL_DIR, FRAMEWORKS_DIR

# -------------------------
# Helpers
# -------------------------
def normalize(name: str) -> str:
    """Normalize strings for filename matching."""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def list_json_files(folder: Path) -> List[str]:
    return [f.name for f in folder.glob("*.json")]

# -------------------------
# Load utilities
# -------------------------
@lru_cache(maxsize=32)
def load_json_file(path: str) -> Optional[dict]:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_all_from_folder(folder: Path) -> Dict[str, dict]:
    """Return a dict filename -> parsed json for all json files in folder."""
    out = {}
    for f in folder.glob("*.json"):
        try:
            out[f.name] = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            out[f.name] = None
    return out

# -------------------------
# Public loaders
# -------------------------
def load_companies() -> Dict[str, dict]:
    return load_all_from_folder(COMPANIES_DIR)

def load_reports() -> Dict[str, dict]:
    return load_all_from_folder(REPORTS_DIR)

def load_news() -> Dict[str, dict]:
    return load_all_from_folder(NEWS_DIR)

def load_social_media() -> Dict[str, dict]:
    return load_all_from_folder(SOCIAL_DIR)

def load_frameworks() -> Dict[str, dict]:
    return load_all_from_folder(FRAMEWORKS_DIR)

# -------------------------
# Detection helpers
# -------------------------
def detect_files_for_company(company_name: str, company_id: str) -> dict:
    """
    Return lists of candidate file paths for reports, news, social for a company.
    Matching uses normalized company name and company_id substrings.
    """
    name_key = normalize(company_name)
    id_key = normalize(company_id)

    def match(fname: str) -> bool:
        nk = normalize(fname)
        return (name_key in nk) or (id_key in nk)

    reports = [str(REPORTS_DIR / f) for f in list_json_files(REPORTS_DIR) if match(f)]
    news = [str(NEWS_DIR / f) for f in list_json_files(NEWS_DIR) if match(f)]
    social = [str(SOCIAL_DIR / f) for f in list_json_files(SOCIAL_DIR) if match(f)]

    return {"reports": reports, "news": news, "social": social}
