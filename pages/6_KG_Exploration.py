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

import streamlit as st
import networkx as nx
from utils.graph_utils import load_graph_json, graph_json_to_networkx
from utils.data_loader import load_companies

st.set_page_config(page_title="Knowledge Graph Explorer", layout="wide")

st.title("🕸 Knowledge Graph Explorer")

# -----------------------------------------------------
# Load full graph
# -----------------------------------------------------
graph_data = load_graph_json()
G = graph_json_to_networkx(graph_data)

# -----------------------------------------------------
# Summary function
# -----------------------------------------------------
def graph_info(G):
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "directed": G.is_directed(),
        "density": nx.density(G),
        "self_loops": nx.number_of_selfloops(G),
    }

# -----------------------------------------------------
# Sidebar selector
# -----------------------------------------------------
st.sidebar.header("Graph Filter Mode")
mode = st.sidebar.selectbox(
    "Select Graph View",
    ["Global Graph", "Company Subgraph"]
)

# -----------------------------------------------------
# COMPANY SUBGRAPH MODE
# -----------------------------------------------------
if mode == "Company Subgraph":
    companies = load_companies()
    company_names = [c["name"] for c in companies.values()]
    
    selected_company = st.sidebar.selectbox("Choose company", company_names)

    # Filter nodes containing company or linked to it
    company_neighbors = set()

    # find neighbors
    for u, v in G.edges():
        if u == selected_company or v == selected_company:
            company_neighbors.add(u)
            company_neighbors.add(v)

    H = G.subgraph(company_neighbors).copy()

    st.write(f"### 📌 Showing subgraph for: **{selected_company}**")
    st.json(graph_info(H))

    st.write("### Edges")
    edges_preview = list(H.edges(data=True))
    st.json(edges_preview[:50])

    st.write("### Nodes")
    nodes_preview = list(H.nodes(data=True))
    st.json(nodes_preview[:50])

# -----------------------------------------------------
# GLOBAL GRAPH MODE
# -----------------------------------------------------
else:
    st.subheader("🌍 Global Knowledge Graph Summary")
    st.json(graph_info(G))

    st.write("### Global Edge Preview (first 50)")
    edges_preview = list(G.edges(data=True))
    st.json(edges_preview[:50])

    st.write("### Global Node Preview (first 50)")
    nodes_preview = list(G.nodes(data=True))
    st.json(nodes_preview[:50])
