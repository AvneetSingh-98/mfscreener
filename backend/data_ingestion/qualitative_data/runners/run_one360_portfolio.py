import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.one360_fund_registry import ONE360_FUND_REGISTRY
from extractors.one360_index_resolver import resolve_one360_sheet
from extractors.one360_portfolio_excel import parse_one360_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\360 ONE\one360_portfolio.xlsx"

AMC = "360 ONE Mutual Fund"
AS_OF = "2025-12-31"

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for fund_key, meta in ONE360_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running 360 ONE fund : {fund_key}")

    sheet_name = meta["keyword"]
    print(f"📄 Sheet resolved : {sheet_name}")

    holdings, section_summary = parse_one360_portfolio_excel(
        XLS_PATH,
        sheet_name
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

    print(f"✅ Done: {fund_key} | Holdings = {len(holdings)} | Top-10 = {top_10_weight}")
