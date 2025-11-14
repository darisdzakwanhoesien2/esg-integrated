import json
import os

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
