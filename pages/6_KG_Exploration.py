# import streamlit as st
# import networkx as nx
# from utils.graph_utils import load_graph_json, graph_json_to_networkx

# st.set_page_config(page_title="Knowledge Graph Explorer", layout="wide")

# st.title("🕸 Knowledge Graph Explorer")

# # -----------------------------------------------------
# # LOAD GRAPH
# # -----------------------------------------------------
# graph_data = load_graph_json()
# G = graph_json_to_networkx(graph_data)

# # -----------------------------------------------------
# # REPLACEMENT FOR nx.info() IN NETWORKX 3.X
# # -----------------------------------------------------
# def graph_info(G: nx.DiGraph):
#     return {
#         "nodes": G.number_of_nodes(),
#         "edges": G.number_of_edges(),
#         "directed": G.is_directed(),
#         "density": nx.density(G),
#         "self_loops": nx.number_of_selfloops(G),
#         "average_degree": (
#             sum(dict(G.degree()).values()) / G.number_of_nodes()
#             if G.number_of_nodes() > 0 else 0
#         )
#     }

# # -----------------------------------------------------
# # GRAPH SUMMARY
# # -----------------------------------------------------
# st.subheader("📊 Graph Summary")
# st.json(graph_info(G))

# # -----------------------------------------------------
# # GRAPH PREVIEW (EDGE LIST)
# # -----------------------------------------------------
# st.subheader("🔗 Graph Preview — First 50 Edges")
# edge_list = []
# for u, v, attrs in list(G.edges(data=True))[:50]:
#     edge_list.append({
#         "source": u,
#         "target": v,
#         "relation": attrs.get("type", "related_to")
#     })

# st.json(edge_list)

# # -----------------------------------------------------
# # OPTIONAL: SHOW NODES
# # -----------------------------------------------------
# with st.expander("📌 Node List (first 50)"):
#     node_preview = list(G.nodes(data=True))[:50]
#     formatted_nodes = [{
#         "node": n,
#         "attributes": attrs
#     } for n, attrs in node_preview]
#     st.json(formatted_nodes)

# pages/6_KG_Exploration.py
import streamlit as st
import json
import networkx as nx
from pyvis.network import Network
from pathlib import Path
import tempfile
from datetime import datetime
import random

from utils.config import MERGED_GRAPH_JSON, KG_DIR
from utils.graph_utils import load_graph_json, graph_json_to_networkx, save_graph_json, structural_summary

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Knowledge Graph Explorer", layout="wide")
st.title("🧠 Knowledge Graph Explorer")

# -----------------------------
# Load merged graph JSON
# -----------------------------
if not MERGED_GRAPH_JSON.exists():
    st.error(
        f"merged_graph.json not found at `{MERGED_GRAPH_JSON}`.\n\n"
        "Please run `python build_graph.py` (or run your graph builder) to generate the file."
    )
    st.stop()

graph_data = load_graph_json(MERGED_GRAPH_JSON)
if not graph_data or not graph_data.get("nodes") or not graph_data.get("edges"):
    st.warning("The merged_graph.json exists but appears empty (no nodes/edges). Run the graph builder.")
    st.stop()

# Build NetworkX DiGraph
G = graph_json_to_networkx(graph_data)

# -----------------------------
# Helper functions
# -----------------------------
def graph_info(G: nx.DiGraph) -> dict:
    """Return a small summary compatible with NetworkX 3.x"""
    n = G.number_of_nodes()
    avg_degree = float(sum(dict(G.degree()).values()) / n) if n > 0 else 0.0
    return {
        "nodes": n,
        "edges": G.number_of_edges(),
        "directed": G.is_directed(),
        "density": float(nx.density(G)),
        "self_loops": int(nx.number_of_selfloops(G)),
        "average_degree": avg_degree
    }

def draw_pyvis_network(H: nx.Graph, show_labels: bool = True, height: str = "700px") -> str:
    """Create a PyVis network from NetworkX graph H and return path to saved HTML file."""
    net = Network(
        height=height,
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
    )
    # physics layout tuned for medium graphs
    net.barnes_hut(gravity=-20000, central_gravity=0.3, spring_length=150, spring_strength=0.02)
    # add nodes
    for node, props in H.nodes(data=True):
        title_lines = []
        title_lines.append(f"<b>{node}</b>")
        if props.get("definition"):
            title_lines.append(props.get("definition"))
        if props.get("domain"):
            title_lines.append(f"<i>{props.get('domain')}</i>")
        title = "<br>".join(title_lines)
        label = node if show_labels else ""
        group = props.get("domain", "Unknown")
        # small tooltip keeps HTML
        net.add_node(node, label=label, title=title, group=group)
    # add edges
    for src, tgt, attrs in H.edges(data=True):
        rel = attrs.get("type", attrs.get("relation", "related_to"))
        net.add_edge(src, tgt, title=rel, label=rel if show_labels else "")
    # save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)
    return tmp.name

def log_merge(old_node: str, new_node: str, merge_log_path: Path = None):
    if merge_log_path is None:
        merge_log_path = Path("merge_log.txt")
    with open(merge_log_path, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {old_node} -> {new_node}\n")

def merge_nodes_in_graph_data(graph_data: dict, old_node: str, new_node: str) -> (dict, bool):
    """
    Merge old_node into new_node in the raw graph_data structure (nodes dict + edges list).
    Returns (updated_graph_data, merged_flag)
    """
    nodes = graph_data.get("nodes", {})
    edges = graph_data.get("edges", [])

    if old_node not in nodes or new_node not in nodes:
        return graph_data, False

    # Merge properties and domain
    old_props = nodes[old_node].get("properties", {})
    new_props = nodes[new_node].get("properties", {})
    merged_props = dict(new_props)  # copy
    merged_props.update(old_props)
    nodes[new_node]["properties"] = merged_props

    if not nodes[new_node].get("domain") and nodes[old_node].get("domain"):
        nodes[new_node]["domain"] = nodes[old_node].get("domain")

    # Redirect edges
    for e in edges:
        if e.get("source") == old_node:
            e["source"] = new_node
        if e.get("target") == old_node:
            e["target"] = new_node

    # Remove old node
    del nodes[old_node]

    # Remove potential duplicate edges (optional: dedupe)
    seen = set()
    deduped = []
    for e in edges:
        key = (e.get("source"), e.get("target"), e.get("type"))
        if key not in seen:
            deduped.append(e)
            seen.add(key)
    graph_data["edges"] = deduped
    graph_data["nodes"] = nodes

    # log
    log_merge(old_node, new_node)
    return graph_data, True

# -----------------------------
# Sidebar: Filters & Controls
# -----------------------------
st.sidebar.header("🔎 Search & Filters")

search_query = st.sidebar.text_input("Search entity name or definition:")
# domain choices from graph_data nodes
domain_choices = sorted({props.get("domain", "Unknown") for props in graph_data["nodes"].values()})
selected_domain = st.sidebar.selectbox("Filter by domain", ["All"] + domain_choices)
show_relations = st.sidebar.checkbox("Show relation labels", value=True)
view_mode = st.sidebar.radio("View mode", ["Global Graph", "Company Subgraph", "Filtered Subgraph"])

# company list extracted from Organization nodes
org_nodes = [n for n, p in graph_data["nodes"].items() if p.get("type", "").lower() in ("organization", "company", "corporate")]
org_nodes_sorted = sorted(org_nodes)

selected_company = None
if view_mode == "Company Subgraph":
    selected_company = st.sidebar.selectbox("Select company", [""] + org_nodes_sorted)

radius = st.sidebar.slider("Ego radius (company subgraph)", min_value=1, max_value=3, value=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🧠 Manual Merge QA")
all_nodes_sorted = sorted(list(graph_data["nodes"].keys()))

old_node = st.sidebar.selectbox("Merge this node (old/duplicate)", [""] + all_nodes_sorted, key="old_node")
new_node = st.sidebar.selectbox("Into this node (canonical)", [""] + all_nodes_sorted, key="new_node")
if st.sidebar.button("🔄 Merge Nodes"):
    if old_node and new_node and old_node != new_node:
        graph_data, merged = merge_nodes_in_graph_data(graph_data, old_node, new_node)
        if merged:
            save_graph_json(graph_data, MERGED_GRAPH_JSON)
            st.sidebar.success(f"Merged '{old_node}' → '{new_node}'. Saved to {MERGED_GRAPH_JSON}")
            st.experimental_rerun()
        else:
            st.sidebar.error("Merge failed — nodes not found.")
    else:
        st.sidebar.warning("Select two distinct nodes to merge.")

if st.sidebar.button("🔁 Refresh Graph (reload file)"):
    st.experimental_rerun()

# Flashcards block (if flashcards.json exists)
st.sidebar.markdown("---")
st.sidebar.subheader("🃏 Flashcard Review")
flashcards_path = Path("flashcards.json")
if flashcards_path.exists():
    with open(flashcards_path, "r", encoding="utf-8") as f:
        flashcards = json.load(f)
    domain_filter = st.sidebar.selectbox("Flashcard domain (optional)", ["All"] + domain_choices)
    if st.sidebar.button("🎴 Show random flashcard"):
        if domain_filter != "All":
            filtered = [c for c in flashcards if domain_filter in c.get("front", "")]
        else:
            filtered = flashcards
        if filtered:
            card = random.choice(filtered)
            st.sidebar.markdown(f"**Q:** {card['front']}")
            if st.sidebar.button("🔁 Reveal answer"):
                st.sidebar.markdown(f"**A:** {card['back']}")
        else:
            st.sidebar.info("No flashcards for selected domain.")
else:
    st.sidebar.info("No flashcards.json file found (optional).")

# -----------------------------
# Build subgraph H based on filters
# -----------------------------
filtered_nodes = []
for node, props in G.nodes(data=True):
    matches_search = True
    if search_query:
        sq = search_query.lower()
        matches_search = (sq in node.lower()) or (sq in str(props.get("definition", "")).lower())
    matches_domain = (selected_domain == "All") or (props.get("domain", "") == selected_domain)

    if matches_search and matches_domain:
        filtered_nodes.append(node)

# Handle view modes
if view_mode == "Company Subgraph" and selected_company:
    if selected_company not in G:
        st.warning(f"Selected company '{selected_company}' not present in graph.")
        H = G.subgraph(filtered_nodes).copy() if filtered_nodes else nx.DiGraph()
    else:
        # ego_graph gives neighbours within radius
        H = nx.ego_graph(G, selected_company, radius=radius, undirected=False, center=True).copy()
        # allow search + domain filtering on H
        if search_query or selected_domain != "All":
            nodes_to_keep = [n for n, p in H.nodes(data=True)
                             if ((search_query.lower() in n.lower() or search_query.lower() in str(p.get("definition","")).lower()) if search_query else True)
                             and (selected_domain == "All" or p.get("domain","") == selected_domain)]
            H = G.subgraph(nodes_to_keep).copy()
elif view_mode == "Filtered Subgraph":
    H = G.subgraph(filtered_nodes).copy()
else:
    # Global
    H = G.copy()

if H.number_of_nodes() == 0:
    st.warning("No nodes match your filters — try widening search or removing domain filter.")
    st.stop()

# -----------------------------
# Show summary + PyVis visualization
# -----------------------------
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("📊 Graph Summary")
    st.json(graph_info(H))
    st.caption("Nodes/edges are for the currently displayed subgraph.")

    if st.button("📈 Structural summary (centrality & communities)"):
        with st.spinner("Computing structural summary..."):
            try:
                summary = structural_summary(MERGED_GRAPH_JSON)
                st.success("Structural summary ready")
                st.json(summary)
            except Exception as e:
                st.error(f"Structural summary failed: {e}")

with col2:
    st.subheader("🔗 Interactive Graph")
    show_labels = show_relations
    html_path = draw_pyvis_network(H, show_labels=show_labels, height="750px")
    # embed
    html = open(html_path, "r", encoding="utf-8").read()
    st.components.v1.html(html, height=750, scrolling=True)

# -----------------------------
# Node details panel (bottom)
# -----------------------------
st.markdown("---")
st.subheader("📌 Node Details (select from displayed nodes)")

displayed_nodes = sorted(list(H.nodes()))
sel_node = st.selectbox("Choose a node to inspect", [""] + displayed_nodes)
if sel_node:
    props = G.nodes[sel_node]
    st.markdown(f"**Entity:** {sel_node}")
    st.markdown(f"**Type:** {props.get('type', 'N/A')}")
    st.markdown(f"**Domain:** {props.get('domain', 'N/A')}")
    st.markdown(f"**Definition:** {props.get('definition', 'N/A')}")
    st.markdown(f"**Description:** {props.get('description', 'N/A')}")
    if props.get("properties"):
        st.markdown("**Properties**")
        st.json(props.get("properties"))

    # show neighbors
    st.markdown("**Outgoing relations**")
    outs = list(G.out_edges(sel_node, data=True))
    st.write([{"target": t, "relation": d.get("type")} for _, t, d in outs][:50])

    st.markdown("**Incoming relations**")
    ins = list(G.in_edges(sel_node, data=True))
    st.write([{"source": s, "relation": d.get("type")} for s, _, d in ins][:50])

st.caption("Tip: Use the sidebar to merge duplicate nodes or to drill down by company or domain.")
