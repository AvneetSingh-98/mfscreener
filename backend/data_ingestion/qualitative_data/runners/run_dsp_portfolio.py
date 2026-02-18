import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.dsp_fund_registry import DSP_FUND_REGISTRY
from extractors.dsp_portfolio_excel import parse_dsp_portfolio_excel

# =====================================================
# CONFIG
# =====================================================

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\DSP\DSP_Portfolio.xlsx"
AMC = "DSP Mutual Fund"
AS_OF = "2025-12-31"

# =====================================================
# DB
# =====================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

# =====================================================
# 🔒 CANONICAL NORMALIZER (LOCKED)
# =====================================================

def normalize_weight_to_percent(w):
    if w is None:
        return None
    w = float(w)
    if 0 < w <= 1:
        return round(w * 100, 4)
    return round(w, 4)

# =====================================================
# RUNNER
# =====================================================

for fund_key, meta in DSP_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running DSP fund : {fund_key}")

    holdings, section_summary = parse_dsp_portfolio_excel(
        XLS_PATH,
        meta["sheet"]
    )

    # 🔒 FINAL NORMALIZATION PASS (NON-NEGOTIABLE)
    for h in holdings:
        h["weight"] = normalize_weight_to_percent(h["weight"])
        h["weight_num"] = normalize_weight_to_percent(h["weight_num"])

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
