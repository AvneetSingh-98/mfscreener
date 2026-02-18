import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.axis_fund_registry import AXIS_FUND_REGISTRY
from extractors.axis_index_resolver import resolve_axis_sheet
from extractors.axis_portfolio_excel import parse_axis_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Axis\Axis_Portfolio.xlsx"

AMC = "Axis Mutual Fund"
AS_OF = "2025-12-31"

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for fund_key, meta in AXIS_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running AXIS fund : {fund_key}")

    sheet_name = resolve_axis_sheet(XLS_PATH, meta["keyword"])
    print(f"📄 Sheet resolved : {sheet_name}")

    holdings, section_summary = parse_axis_portfolio_excel(
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

    print(f"✅ Done: {fund_key} | Holdings = {len(holdings)}")
