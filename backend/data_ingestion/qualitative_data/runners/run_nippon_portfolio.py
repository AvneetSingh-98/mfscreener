import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.nippon_fund_registry import NIPPON_FUND_REGISTRY
from extractors.nippon_index_resolver import build_index_map, resolve_sheet_code
from extractors.nippon_excel import parse_nippon_sheet

# =========================
# CONFIG
# =========================

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Nippon India\Nippon-Portfolio.xls"
AMC = "Nippon India Mutual Fund"
AS_OF = "2025-12-31"

# =========================
# DB
# =========================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]   # 🔒 Locked collection

# =========================
# BUILD INDEX MAP
# =========================

index_map = build_index_map(XLS_PATH)

# =========================
# TOP 10 (EQUITY ONLY)
# =========================

def compute_top_10_equity_weight(holdings):

    weights = [
        h["weight_num"]
        for h in holdings
        if h.get("section") == "equity"
        and isinstance(h.get("weight_num"), (int, float))
        and 0 < h["weight_num"] <= 100
    ]

    if not weights:
        return 0.0

    top_10 = round(sum(sorted(weights, reverse=True)[:10]), 2)

    if not (0 < top_10 <= 100):
        raise ValueError(f"❌ Invalid Top-10 Equity Weight: {top_10}")

    return top_10

# =========================
# RUN ALL FUNDS
# =========================

for fund_key, meta in NIPPON_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running NIPPON fund : {fund_key}")

    # ---------- SHEET RESOLUTION ----------
    if "sheet" in meta:
        sheet_code = meta["sheet"]
    else:
        sheet_code = resolve_sheet_code(
            index_map,
            meta["canonical_name"]
        )

    print(f"📄 Sheet used         : {sheet_code}")

    # ---------- PARSE ----------
    holdings, section_summary = parse_nippon_sheet(
        XLS_PATH,
        sheet_code
    )

    print(f"📊 Holdings parsed    : {len(holdings)}")

    # ---------- TOP 10 ----------
    top_10_weight = compute_top_10_equity_weight(holdings)

    # ---------- MONGO DOCUMENT ----------
    doc = {
        "fund_key": fund_key,
        "amc": AMC,
        "category": meta["category"],
        "asset_class": meta.get("asset_class", "Equity"),
        "sheet_code": sheet_code,
        "as_of": AS_OF,

        "holdings": holdings,
        "section_summary": section_summary,

        "counts": {
            "total": len(holdings)
        },

        "top_10_weight": top_10_weight,
        "ingested_at": datetime.utcnow()
    }

    # ---------- UPSERT ----------
    col.update_one(
        {
            "fund_key": fund_key,
            "amc": AMC,
            "as_of": AS_OF
        },
        {"$set": doc},
        upsert=True
    )

    print(
        f"✅ Done: {fund_key} | "
        f"Holdings = {len(holdings)} | "
        f"Top-10 = {top_10_weight}"
    )
