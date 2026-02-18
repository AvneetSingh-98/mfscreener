import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.uti_fund_registry import UTI_FUND_REGISTRY
from extractors.uti_portfolio_excel import parse_uti_portfolio_excel


# =====================
# CONFIG
# =====================
XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\UTI\UTI_Portfolio.xlsx"
AMC = "UTI Mutual Fund"
AS_OF = "2025-12-31"


# =====================
# DB
# =====================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]


# =====================
# RUN
# =====================
for fund_key, meta in UTI_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running UTI fund : {fund_key}")

    # --- SAFETY: validate registry ---
    if "scheme_code" not in meta:
        print(f"⚠️ Skipping {fund_key}: scheme_code missing in registry")
        continue

    try:
        holdings, section_summary = parse_uti_portfolio_excel(
            XLS_PATH,
            scheme_code=meta["scheme_code"]
        )
    except Exception as e:
        # Critical: do NOT crash the whole run
        print(f"⚠️ Skipping {fund_key}: {e}")
        continue

    # --- TOP 10 EQUITY CONCENTRATION ---
    equity_weights = [
        h.get("weight_num", 0)
        for h in holdings
        if h.get("section") == "equity"
    ]

    top_10_weight = round(
        sum(sorted(equity_weights, reverse=True)[:10]),
        2
    )

    # --- UPSERT ---
    col.update_one(
        {
            "fund_key": fund_key,
            "amc": AMC,
            "as_of": AS_OF
        },
        {
            "$set": {
                "fund_key": fund_key,
                "amc": AMC,
                "category": meta.get("category"),
                "asset_class": meta.get("asset_class"),
                "as_of": AS_OF,
                "holdings": holdings,
                "section_summary": section_summary,
                "counts": {
                    "total": len(holdings)
                },
                "top_10_weight": top_10_weight,
                "ingested_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print(
        f"✅ Done: {fund_key} | "
        f"Holdings = {len(holdings)} | "
        f"Top-10 = {top_10_weight}"
    )

print("\n🎉 UTI portfolio ingestion completed")
