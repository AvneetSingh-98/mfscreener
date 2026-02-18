# backend/data_ingestion/qualitative_data/runners/run_ppfas_portfolio.py

import sys
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.ppfas_fund_registry import PPFAS_FUND_REGISTRY
from extractors.ppfas_portfolio_excel import parse_ppfas_portfolio_excel

# -------------------------
# CONFIG
# -------------------------

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\PPFAS\PPFAS-Portfolio.xls"
AS_OF = "2025-12-31"
AMC = "PPFAS Mutual Fund"

# -------------------------
# DB
# -------------------------

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

# -------------------------
# FUNDS TO RUN
# -------------------------

fund_keys = (
    [sys.argv[1]] if len(sys.argv) == 2
    else list(PPFAS_FUND_REGISTRY.keys())
)

# -------------------------
# RUN
# -------------------------

for fund_key in fund_keys:

    meta = PPFAS_FUND_REGISTRY[fund_key]
    sheet = meta["sheet"]

    print("\n" + "=" * 60)
    print(f"🚀 Running PPFAS fund : {fund_key}")
    print(f"📄 Sheet used        : {sheet}")

    # ---------- PARSE ----------
    holdings, section_summary = parse_ppfas_portfolio_excel(
        XLS_PATH, sheet
    )

    # ---------- TOP 10 (EQUITY ONLY) ----------
    equity_weights = [
        h["weight_num"]
        for h in holdings
        if h.get("section") in ("equity", "equity_foreign")
    ]

    top_10_weight = round(
        sum(sorted(equity_weights, reverse=True)[:10]),
        2
    )

    # ---------- MONGO WRITE ----------
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
