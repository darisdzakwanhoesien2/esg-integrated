# utils/esg_mapping_utils.py
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from .config import FRAMEWORKS_DIR

# -------------------------
# Load framework registries
# -------------------------
def load_framework_registry(name: str) -> Optional[dict]:
    """
    Load a framework JSON by file stem. Example names: 'GRI_v2021', 'UNSDG_schema'
    """
    path = FRAMEWORKS_DIR / f"{name}.json"
    if not path.exists():
        # try any file that contains the name
        for f in FRAMEWORKS_DIR.glob("*.json"):
            if name.lower() in f.stem.lower():
                path = f
                break
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

# -------------------------
# Simple mapping helpers
# -------------------------
def map_report_metrics_to_gri(report: dict, gri_registry: dict) -> Dict[str, dict]:
    """
    Attempt to map report metrics (report['metrics']) to GRI metrics by
    simple substring matching between metric keys and GRI titles/ids.
    Returns dictionary of matches {gri_id: {covered: bool, extracted_metric: {...}}}
    """
    matches = {}
    metrics = report.get("metrics", {})
    for gri_item in gri_registry.get("standards", []):
        gid = gri_item.get("standard_id") or gri_item.get("id") or gri_item.get("code")
        title = (gri_item.get("title") or "").lower()
        for mkey, mval in metrics.items():
            if mkey.lower() in title or any(tok in title for tok in mkey.lower().split("_")):
                matches[gid] = {
                    "covered": True,
                    "extracted_metric": {"value": mval, "unit": None},
                    "confidence": 0.7,
                    "match_on": mkey
                }
    return matches

def map_report_to_unsdg(report: dict, unsdg_registry: dict) -> Dict[str, Any]:
    """
    Very simple mapping: match report topics -> SDG targets by keyword overlap.
    Returns structure {sdg_id: {target_id: {covered: bool, evidence: [...]}}}
    """
    out = {}
    # compile list of reported topics (flat)
    topics = []
    for cat, tlist in report.get("esg_topics", {}).items():
        topics.extend([t.lower() for t in tlist])
    for sdg in unsdg_registry.get("sdgs", []):
        sdg_id = sdg.get("sdg_id")
        out[sdg_id] = {}
        for target in sdg.get("targets", []):
            tgt_id = target.get("target_id")
            text = (target.get("text") or "").lower()
            for tp in topics:
                if tp in text or any(tok in text for tok in tp.split()):
                    out[sdg_id][tgt_id] = {
                        "covered": True,
                        "evidence": [f"topic_match:{tp}"],
                        "confidence": 0.5
                    }
    return out

def build_framework_alignment(report: dict, frameworks: Dict[str, dict]) -> Dict[str, dict]:
    """
    Convenience function to generate a lightweight framework_alignment for a report.
    frameworks is a dict like {'GRI': <json>, 'UNSDG': <json>, 'SASB': <json>}
    """
    alignment = {}
    if "GRI" in frameworks:
        alignment["GRI"] = map_report_metrics_to_gri(report, frameworks["GRI"])
    if "UNSDG" in frameworks:
        alignment["UNSDG"] = map_report_to_unsdg(report, frameworks["UNSDG"])
    # SASB mapping can be added similarly if registry provided
    return alignment
