
1. Populate indicators with the official UN indicator IDs for each target (the global indicator list is separate and I can add it).
2. Produce a CSV crosswalk between SDG targets and corporate KPIs (useful to auto-map report metrics to SDG targets).
3. Map example company metrics (from your sample companies) to specific SDG targets (automatically annotate Company A/B/C with the SDG targets they touch).
4. Add local-provider crosswalks linking SDG targets to country-specific priorities (e.g., Finland, Sweden, Japan).

BATCH 3 — /data/social_media for 3 companies
1. Twitter, LinkedIn, Reddit samples
2. Multiple posts, comments, analysis included.

BATCH 4 — ESG Frameworks (GRI, UNSDG, SASB, Local FIN-ESG)
1. Provide complete root structures
2. UNSDG: all 17 SDGs + 169 targets (if you want the full list, confirm)
GRI full version
SASB: 3 industries (for A/B/C)
FIN-ESG local regulation
Already included UNSDG full list

BATCH 5 — /external_data + /kg_exports sample
1. Satellite emissions (dummy)
2. Market data (dummy)
3. Neo4j nodes.csv, rels.csv sample
4. NetworkX pickle structure example
Weather & climate data
Supply chain records

B) /data/frameworks/



3) Generate a class-based ESGDataLoader (cleaner architecture)?



A) /data/news for all 3 companies (full, multi-source news set)
B) /data/frameworks (GRI, SASB, FIN-ESG) full detailed versions
C) /data/external_data (satellite emissions + market data)
D) /data/kg_exports with ready-to-import Neo4j nodes.csv + relations.csv


3. Generate UNSDG_schema.json as a downloadable file inside the repo layout and add it under /data/frameworks/ (I can produce the file text for you to paste).

A) Add charts

sentiment trendline

ESG topic bar charts

news vs social sentiment comparison

GRI/SDG coverage gauge visualization

B) PyVis interactive KG viewer

Loads networkx_graph.pkl and displays a full ESG knowledge graph.

C) Company comparison dashboard

Side-by-side metrics & sentiment comparison.

D) Add caching + faster loading

Use @st.cache_data for JSON loads.

E) Deploy configuration

Dockerfile + VPS or Streamlit Cloud deployment script.

                    ┌───────────────────────┐
                    │       Company A       │
                    └───────┬───────────────┘
                            │
                            ▼
           ┌──────────────────────────────────────┐
           │      Sustainability Report 2023       │
           └───────┬──────────┬────────────┬──────┘
                   │          │            │
                   ▼          ▼            ▼
               Metric      Topic        Claim
                               │            │
                               ▼            │
                       SDG_Target ◄─────────┘
                               │
                               ▼
                          SDG_Goal

                    (News 2024)
                            │
     ┌───────────── SUPPORTS / CONTRADICTS ─────────────┐
                            ▼                            │
                        News Article                     │
                            │                            │
                            ▼                            │
                       ESG Finding  ◄───────LINK─────────┘
                            ▼
                       Risk Signal

                         (Social Media 2024)
                                    │
                                    ▼
                                  Post
                                    │
                                    ▼
                               Social Signal
                                    │
                                    ▼
                                  Topic



esg_dashboard/
│
├── streamlit_app.py                    # Main launcher
├── pages/
│   ├── 1_Company_Overview.py
│   ├── 2_Reports_Explorer.py
│   ├── 3_Social_Media_Insights.py
│   ├── 4_News_Analytics.py
│   ├── 5_Framework_Compliance.py
│   ├── 6_KG_Exploration.py
│   └── 7_Comparisons.py
│
├── components/
│   ├── cards.py               # Custom UI components
│   ├── charts.py              # Reusable chart generation
│   ├── layout.py              # Custom layout helpers
│   └── tables.py              # Reusable tables
│
├── utils/
│   ├── data_loader.py         # Loads JSON from /data
│   ├── aggregations.py        # Summary stats
│   ├── esg_mapping_utils.py   # GRI / SDG / SASB alignment
│   ├── graph_utils.py         # NetworkX + Neo4j connectors
│   └── config.py              # File paths, constants
│
├── assets/
│   ├── logo.png
│   ├── styles.css
│   └── icons/


esg-kg-project/
├── README.md
├── LICENSE
├── data/                       # SYMLINK / COPY FROM MAIN PROJECT
│   ├── companies/
│   │   └── companyA.json
│   ├── reports/
│   │   └── companyA_2023_report.json
│   ├── frameworks/
│   │   ├── GRI_v2021.json
│   │   ├── SASB_registry.json
│   │   ├── UNSDG_schema.json
│   │   └── LOCAL/
│   │       └── FIN-ESG.json
│   ├── news/
│   │   └── news_2024_companyA.json
│   ├── social_media/
│   │   └── socialMedia_2024_companyA.json
│   ├── external_data/
│   │   ├── satellite_emissions/
│   │   └── market_data/
│   └── kg_exports/
│       ├── neo4j_import.csv
│       └── networkx_graph.pkl
│
├── ingestion/
│   ├── fetchers/
│   │   ├── news_fetcher.py
│   │   ├── social_fetcher_twitter.py
│   │   └── social_fetcher_linkedin.py
│   ├── pdf_parser/
│   │   ├── pdf_text_extractor.py
│   │   └── pdf_layout_parser.py
│   └── transform/
│       └── normalizers.py
│
├── extraction/
│   ├── nlp/
│   │   ├── ner.py
│   │   ├── claim_extraction.py
│   │   ├── metric_extraction.py
│   │   └── topic_modeling.py
│   ├── esg_mapping/
│   │   ├── gri_mapper.py
│   │   ├── sasb_mapper.py
│   │   └── unsdg_mapper.py
│   └── classifiers/
│       ├── sentiment.py
│       └── esg_category_classifier.py
│
├── analysis/
│   ├── time_series/
│   │   └── trends.py
│   ├── comparisons/
│   │   └── cross_company.py
│   ├── compliance_scoring/
│   │   └── score.py
│   └── risk_detection/
│       └── early_warning.py
│
├── kg/
│   ├── build_kg.py
│   ├── neo4j/
│   │   ├── import_nodes.csv
│   │   └── import_rels.csv
│   └── networkx/
│       └── export_graph.py
│
├── models/
│   ├── sentiment_model/
│   ├── claim_extractor/
│   └── topic_model/
│
├── notebooks/
│   ├── 01_ingest_and_preview.ipynb
│   ├── 02_extraction_pipeline.ipynb
│   └── 03_graph_analysis.ipynb
│
├── dashboards/
│   ├── streamlit_app.py
│   └── dashboard_assets/
│
├── services/
│   ├── api/
│   │   ├── app.py
│   │   └── routes.py
│   └── workers/
│       └── transform_worker.py
│
├── scripts/
│   ├── run_all.sh
│   ├── build_neo4j_import.sh
│   └── deploy_dashboard.sh
│
└── tests/
    ├── unit/
    └── integration/
# esg-integrated
