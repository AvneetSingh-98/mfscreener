import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

map_col = db["scheme_benchmark_map"]   # CRISIL source
fund_map_col = db["fund_benchmark_map"]

fund_map_col.delete_many({})  # one-time rebuild (safe)

def normalize_fund_name(name: str) -> str:
    name = name.lower()
    for t in [
        "direct", "regular", "growth", "idcw", "dividend",
        "plan", "option", "fund"
    ]:
        name = name.replace(t, "")
    return " ".join(name.split())


seen = set()

for row in map_col.find({}):
    base_name = normalize_fund_name(row["scheme_name"])

    if base_name in seen:
        continue

    fund_map_col.insert_one({
        "fund_key": base_name,
        "benchmark": row["benchmark"],
        "category": row.get("category"),
        "source": "CRISIL",
        "created_at": datetime.utcnow()
    })

    seen.add(base_name)

print("✅ fund_benchmark_map built")
print("Funds mapped:", fund_map_col.count_documents({}))
