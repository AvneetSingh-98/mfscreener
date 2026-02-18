import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.bandhan_fund_registry import BANDHAN_FUND_REGISTRY
from extractors.bandhan_portfolio_excel import parse_bandhan_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Bandhan\Bandhan_Portfolio.xlsx"

AMC = "Bandhan Mutual Fund"
AS_OF = "2025-12-31"

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for fund_key, meta in BANDHAN_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running BANDHAN fund : {fund_key}")

    holdings, section_summary = parse_bandhan_portfolio_excel(
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
        2
    )

    # 🔒 SANITY CHECK
    if top_10_weight > 100:
        raise ValueError(
            f"❌ Top-10 > 100 detected for {fund_key}: {top_10_weight}"
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
        f"✅ Done: {fund_key} | "
        f"Holdings = {len(holdings)} | "
        f"Top-10 = {top_10_weight}"
    )
