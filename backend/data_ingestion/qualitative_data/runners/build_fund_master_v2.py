import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime
from extractors.ppfas_fund_registry import PPFAS_FUND_REGISTRY

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
fund_benchmark_col = db["fund_benchmark_map_v2"]


for fund_id, meta in PPFAS_FUND_REGISTRY.items():
    fund_benchmark_col.update_one(
        {"fund_id": fund_id},
        {"$set": {
            "fund_id": fund_id,
            "amc": "PPFAS Mutual Fund",
            "canonical_name": meta["canonical_name"],
            "category": meta["category"],
            "asset_class": meta["asset_class"],
            "active": True,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

print("✅ fund_master_v2 built")
