import streamlit as st
import networkx as nx
from utils.graph_utils import load_graph

st.title("🕸 Knowledge Graph Explorer")

G = load_graph()

st.write("### Graph Info")
st.write(nx.info(G))

st.write("### Graph Preview (edge list)")
edge_list = list(G.edges(data=True))[:50]
st.json(edge_list)
