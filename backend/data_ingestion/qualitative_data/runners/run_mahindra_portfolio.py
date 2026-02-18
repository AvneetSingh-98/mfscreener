import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.mahindra_portfolio_excel import parse_mahindra_fund
from extractors.mahindra_fund_registry import MAHINDRA_FUND_REGISTRY

# ============================
# CONFIG
# ============================

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Mahindra Manulife\Mahindra_Portfolio.xlsx"

AMC = "Mahindra Manulife Mutual Fund"
AS_OF = "2025-12-31"

# ============================
# DB
# ============================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

# ============================
# RUNNER
# ============================

for fund_key, meta in MAHINDRA_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running MAHINDRA fund : {fund_key}")

    holdings, section_summary = parse_mahindra_fund(
        XLS_PATH,
        meta["sheet"]
    )

    equity_weights = [
        h["weight_num"]
        for h in holdings
        if h["section"] == "equity"
    ]

    top_10_weight = round(
        sum(sorted(equity_weights, reverse=True)[:10]),
        4
    )

    col.update_one(
        {"fund_key": fund_key, "amc": AMC, "as_of": AS_OF},
        {"$set": {
            "fund_key": fund_key,
            "amc": AMC,
            "category": meta["category"],
            "asset_class": meta["asset_class"],
            "as_of": AS_OF,
            "holdings": holdings,
            "section_summary": section_summary,
            "counts": {"total": len(holdings)},
            "top_10_weight": top_10_weight,
            "ingested_at": datetime.utcnow()
        }},
        upsert=True
    )

    print(
        f"✅ Done: {fund_key} | Holdings = {len(holdings)} | "
        f"Top-10 Equity = {top_10_weight}"
    )
