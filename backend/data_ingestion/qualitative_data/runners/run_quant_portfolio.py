import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.quant_fund_registry import QUANT_FUND_REGISTRY
from extractors.quant_portfolio_excel import parse_quant_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Quant\Quant_Portfolio.xlsx"
AS_OF = "2025-12-31"
AMC = "quant Mutual Fund"

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for fund_key, meta in QUANT_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running QUANT fund : {fund_key}")

    holdings, segregation_summary = parse_quant_portfolio_excel(
        XLS_PATH, meta["sheet"]
    )

    top10 = round(
        sum(
            h["weight"]
            for h in sorted(holdings, key=lambda x: x["weight"], reverse=True)[:10]
        ),
        2
    )

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
                "category": meta["category"],
                "asset_class": meta["asset_class"],
                "as_of": AS_OF,

                "holdings": holdings,
                "segregation_summary": segregation_summary,
                "counts": { "total": len(holdings) },

                "top_10_weight": top10,
                "ingested_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print(f"✅ Done: {fund_key} | Holdings = {len(holdings)}")
