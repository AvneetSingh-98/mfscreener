from pymongo import MongoClient
from datetime import datetime

from extractors.iti_fund_registry import ITI_FUND_REGISTRY
from extractors.iti_index_resolver import resolve_iti_sheet
from extractors.iti_portfolio_excel import parse_iti_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-11\ITI\ITI_Portfolio.xlsx"

AMC = "ITI Mutual Fund"
AS_OF = "2025-11-30"

client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for fund_key, meta in ITI_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running ITI fund : {fund_key}")

    sheet = resolve_iti_sheet(XLS_PATH, meta["keyword"])
    print(f"📄 Sheet resolved : {sheet}")

    holdings, section_summary = parse_iti_portfolio_excel(
        XLS_PATH, sheet
    )

    equity_weights = [
        h["weight_num"]
        for h in holdings
        if h["section"] == "equity"
    ]

    top_10_weight = round(
        sum(sorted(equity_weights, reverse=True)[:10]), 2
    )

    col.replace_one(
        {"fund_key": fund_key, "amc": AMC, "as_of": AS_OF},
        {"fund_key": fund_key,
         "amc": AMC,
         "category": meta["category"],
         "asset_class": meta["asset_class"],
         "as_of": AS_OF,
         "holdings": holdings,
         "section_summary": section_summary,
         "counts": {"total": len(holdings)},
         "top_10_weight": top_10_weight,
         "ingested_at": datetime.utcnow()
        },
        upsert=True
    )

    print(f"✅ Done: {fund_key} | Holdings = {len(holdings)}")
