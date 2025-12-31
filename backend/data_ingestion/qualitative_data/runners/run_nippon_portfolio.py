from pymongo import MongoClient
from datetime import datetime

from extractors.nippon_fund_registry import NIPPON_FUND_REGISTRY
from extractors.nippon_index_resolver import build_index_map, resolve_sheet_code
from extractors.nippon_excel import parse_nippon_sheet

# =========================
# CONFIG
# =========================
XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-11\Nippon India\Nippon-Portfolio.xlsx"
AMC = "Nippon India Mutual Fund"
AS_OF = "2025-11-30"

# =========================
# DB
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]   # ✅ Phase-4 only

# =========================
# BUILD INDEX MAP
# =========================
index_map = build_index_map(XLS_PATH)

# =========================
# RUN ALL FUNDS
# =========================
for fund_key, meta in NIPPON_FUND_REGISTRY.items():

    print("=" * 60)
    print(f"🚀 Running NIPPON fund : {fund_key}")

    # 🔒 HARD OVERRIDE IF PRESENT
    if "sheet" in meta:
        sheet_code = meta["sheet"]
    else:
        sheet_code = resolve_sheet_code(index_map, meta["canonical_name"])

    print(f"📄 Sheet used         : {sheet_code}")

    # ---------- PARSE ----------
    holdings = parse_nippon_sheet(XLS_PATH, sheet_code)

    print(f"📊 Holdings parsed    : {len(holdings)}")

    # ---------- TOP 10 ----------
    top_10_weight = round(
        sum(
            h["weight"]
            for h in sorted(holdings, key=lambda x: x["weight"], reverse=True)[:10]
        ),
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
                "sheet_code": sheet_code,
                "as_of": AS_OF,
                "holdings": holdings,
                "counts": {
                    "total": len(holdings)
                },
                "top_10_weight": top_10_weight,
                "ingested_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    print(f"✅ Done: {fund_key} | Top-10 = {top_10_weight}")
