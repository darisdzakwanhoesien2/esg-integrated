# utils/graph_utils.py
import json
from typing import Dict, Any, Tuple, List
from pathlib import Path
import networkx as nx
from networkx.readwrite import json_graph
from .config import MERGED_GRAPH_JSON, KG_DIR
from collections import defaultdict

# -------------------------
# Basic IO
# -------------------------
def load_graph_json(path: Path = None) -> Dict[str, Any]:
    if path is None:
        path = MERGED_GRAPH_JSON
    if not path.exists():
        return {"nodes": {}, "edges": []}
    return json.loads(path.read_text(encoding="utf-8"))

def save_graph_json(graph_data: Dict[str, Any], path: Path = None) -> None:
    if path is None:
        path = MERGED_GRAPH_JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph_data, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------
# Convert to NetworkX
# -------------------------
def graph_json_to_networkx(graph_data: Dict[str, Any]) -> nx.DiGraph:
    G = nx.DiGraph()
    nodes = graph_data.get("nodes", {})
    for node_name, props in nodes.items():
        # store all props as node attributes
        G.add_node(node_name, **props)
    for e in graph_data.get("edges", []):
        src = e.get("source")
        tgt = e.get("target")
        typ = e.get("type", "related_to")
        if src is None or tgt is None:
            continue
        G.add_edge(src, tgt, type=typ)
    return G

def networkx_to_graph_json(G: nx.Graph) -> Dict[str, Any]:
    graph_data = {"nodes": {}, "edges": []}
    for n, attrs in G.nodes(data=True):
        graph_data["nodes"][n] = attrs
    for u, v, attrs in G.edges(data=True):
        graph_data["edges"].append({"source": u, "target": v, "type": attrs.get("type", "related_to")})
    return graph_data

# -------------------------
# Build a simple graph from the ESG data directories
# -------------------------
def build_graph_from_data(companies: Dict[str, dict],
                          reports: Dict[str, dict],
                          news: Dict[str, dict],
                          social: Dict[str, dict]) -> Dict[str, Any]:
    """
    Lightweight auto-builder. Creates nodes for companies, report topics, news topics,
    social topics, frameworks (if present) and edges connecting them.
    """
    graph = {"nodes": {}, "edges": []}

    def add_node(key: str, props: dict):
        if key not in graph["nodes"]:
            graph["nodes"][key] = props

    def add_edge(s: str, t: str, rel: str):
        graph["edges"].append({"source": s, "target": t, "type": rel})

    # Companies
    for fname, comp in companies.items():
        name = comp.get("name")
        add_node(name, {
            "entity": name,
            "type": "Organization",
            "domain": "Corporate",
            "definition": comp.get("description", comp.get("sector", "")),
            "properties": comp.get("identifiers", {})
        })

    # Reports -> topics/metrics
    for fname, rpt in reports.items():
        cname = rpt.get("company") or rpt.get("company_id") or fname.split("_")[0]
        cname = cname if isinstance(cname, str) else str(cname)
        if isinstance(rpt.get("esg_topics"), dict):
            for cat, topics in rpt.get("esg_topics", {}).items():
                for t in topics:
                    add_node(t, {"entity": t, "type": "ESG Topic", "domain": cat})
                    add_edge(cname, t, "reports_on")
        # metrics as nodes
        for mkey, mval in rpt.get("metrics", {}).items():
            metric_node = f"{cname}::{mkey}"
            add_node(metric_node, {"entity": mkey, "type": "Metric", "domain": "Metric", "properties": {"value": mval}})
            add_edge(cname, metric_node, "reports_metric")

    # News -> topics
    for fname, newsf in news.items():
        # for each article, create article node and link to company/topics
        for src in newsf.get("news_sources", []):
            for art in src.get("articles", []):
                art_id = art.get("article_id") or art.get("title")[:60]
                art_node = f"article::{art_id}"
                add_node(art_node, {"entity": art.get("title"), "type": "NewsArticle", "domain": src.get("source_type")})
                # link to topics
                for t in art.get("analysis", {}).get("esg_topics", []):
                    add_node(t, {"entity": t, "type": "ESG Topic", "domain": "Environment"})
                    add_edge(art_node, t, "mentions")
                # optionally link to company if company name appears in title or content
                for comp_name in [c.get("name") for c in companies.values()]:
                    if comp_name and comp_name.lower() in (art.get("content_cleaned","") or "").lower():
                        add_edge(art_node, comp_name, "mentions_company")

    # Social -> posts linking to topics
    for fname, socialf in social.items():
        for platform in socialf.get("platforms", []):
            for post in platform.get("posts", []):
                pid = post.get("post_id") or post.get("content_raw","")[:40]
                post_node = f"post::{pid}"
                add_node(post_node, {"entity": post.get("content_raw","")[:140], "type": "SocialPost", "domain": platform.get("platform")})
                for t in post.get("analysis", {}).get("esg_topics", []):
                    add_node(t, {"entity": t, "type": "ESG Topic", "domain": "Environment"})
                    add_edge(post_node, t, "mentions")

    return graph

# -------------------------
# Structural summary
# -------------------------
def structural_summary(graph_path: Path = None) -> dict:
    """
    Quick structural statistics (nodes, edges, degree centrality, communities).
    """
    d = load_graph_json(graph_path) if graph_path else load_graph_json()
    G = graph_json_to_networkx(d)
    summary = {}
    summary["nodes"] = G.number_of_nodes()
    summary["edges"] = G.number_of_edges()
    # top degree central nodes
    deg = sorted(G.degree, key=lambda x: x[1], reverse=True)[:20]
    summary["top_degree"] = [{"node": n, "degree": int(k)} for n,k in deg]
    # top in_degree and out_degree
    indeg = sorted(G.in_degree, key=lambda x: x[1], reverse=True)[:10]
    outdeg = sorted(G.out_degree, key=lambda x: x[1], reverse=True)[:10]
    summary["top_indegree"] = [{"node": n, "value": int(k)} for n,k in indeg]
    summary["top_outdegree"] = [{"node": n, "value": int(k)} for n,k in outdeg]
    # basic connected components (on undirected version)
    und = G.to_undirected()
    components = list(nx.connected_components(und))
    summary["components_count"] = len(components)
    # communities using greedy modularity if graph not too large
    try:
        from networkx.algorithms import community
        comms = list(community.greedy_modularity_communities(und))
        summary["communities"] = [list(c)[:10] for c in comms[:10]]
    except Exception:
        summary["communities"] = []
    return summary
