import json
from utils.data_loader import load_companies, load_reports, load_news, load_social_media
from utils.graph_utils import build_graph_from_data, save_graph_json
from utils.config import KG_DIR, MERGED_GRAPH_JSON

print("🔄 Loading ESG data...")

companies = load_companies()
reports = load_reports()
news = load_news()
social = load_social_media()

print("📈 Building Knowledge Graph...")
graph = build_graph_from_data(companies, reports, news, social)

print(f"💾 Saving to {MERGED_GRAPH_JSON} ...")
save_graph_json(graph, MERGED_GRAPH_JSON)

print("✅ Done! merged_graph.json generated.")
