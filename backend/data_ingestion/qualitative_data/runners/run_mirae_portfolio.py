import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

from extractors.mirae_sheet_resolver import resolve_mirae_sheet
from extractors.mirae_portfolio_excel import parse_mirae_portfolio

# =====================
# CONFIG
# =====================

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-12\Mirae Asset\Mirae_Portfolio.xlsx"
AS_OF = "2025-12-31"
AMC = "Mirae Asset Mutual Fund"

FUNDS = [

    # ---------------- Sectoral / Thematic ----------------
    {"fund_key": "MIRAE_INFRASTRUCTURE", "sheet": "Infrastructure Fund", "category": "Sectoral / Thematic"},
    {"fund_key": "MIRAE_BANKING_FIN_SERV", "sheet": "Banking & Financial Services", "category": "Sectoral / Thematic"},
    {"fund_key": "MIRAE_HEALTHCARE", "sheet": "Healthcare Fund", "category": "Sectoral / Thematic"},
    {"fund_key": "MIRAE_CONSUMER", "sheet": "Consumer Fund", "category": "Sectoral / Thematic"},
    {"fund_key": "MIRAE_MANUFACTURING", "sheet": "Manufacturing Fund", "category": "Sectoral / Thematic"},

    # ---------------- Core Equity ----------------
    {"fund_key": "MIRAE_LARGE_CAP", "sheet": "Large Cap Fund", "category": "Large Cap"},
    {"fund_key": "MIRAE_LARGE_MID_CAP", "sheet": "Large & Midcap Fund", "category": "Large & Mid Cap"},
    {"fund_key": "MIRAE_MID_CAP", "sheet": "Mid Cap Fund", "category": "Mid Cap"},
    {"fund_key": "MIRAE_SMALL_CAP", "sheet": "Small Cap Fund", "category": "Small Cap"},
    {"fund_key": "MIRAE_FLEXI_CAP", "sheet": "Flexi Cap Fund", "category": "Flexi Cap"},
    {"fund_key": "MIRAE_FOCUSED", "sheet": "Focused", "category": "Focused"},
    {"fund_key": "MIRAE_ELSS", "sheet": "ELSS", "category": "ELSS"},

    # ---------------- Hybrid ----------------
    {"fund_key": "MIRAE_BALANCED_ADVANTAGE", "sheet": "Balanced Advantage", "category": "Balanced Advantage"},
    {"fund_key": "MIRAE_EQUITY_HYBRID", "sheet": "Aggressive Hybrid", "category": "Aggressive Hybrid"},
    {"fund_key": "MIRAE_MULTI_ASSET", "sheet": "Multi Asset Allocation", "category": "Multi Asset Allocation"},

    # ---------------- Other Equity ----------------
    {"fund_key": "MIRAE_EQUITY_SAVINGS", "sheet": "Equity Savings", "category": "Equity Savings"},
]

# =====================
# DB
# =====================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

# =====================
# TOP 10 CALCULATION
# =====================

def compute_top_10_equity_weight(holdings):

    weights = [
        h["weight_num"]
        for h in holdings
        if h.get("section") == "equity"
    ]

    if not weights:
        return 0.0

    # Mirae often gives fractional weights
    if max(weights) <= 1:
        weights = [w * 100 for w in weights]

    return round(sum(sorted(weights, reverse=True)[:10]), 2)

# =====================
# RUNNER
# =====================

for meta in FUNDS:

    print("=" * 60)
    print(f"🚀 Running Mirae fund : {meta['fund_key']}")

    sheet = resolve_mirae_sheet(XLS_PATH, meta["sheet"])
    print(f"📄 Sheet used : {sheet}")

    # 🔥 FIXED LINE
    holdings, section_summary = parse_mirae_portfolio(
        XLS_PATH,
        sheet
    )

    if not holdings:
        print(f"⚠️ No holdings found for {meta['fund_key']}")
        continue

    top_10_weight = compute_top_10_equity_weight(holdings)

    doc = {
        "fund_key": meta["fund_key"],
        "amc": AMC,
        "as_of": AS_OF,
        "asset_class": "Equity",
        "category": meta["category"],
        "holdings": holdings,
        "section_summary": section_summary,
        "counts": {"total": len(holdings)},
        "top_10_weight": top_10_weight,
        "ingested_at": datetime.utcnow()
    }

    col.replace_one(
        {"fund_key": meta["fund_key"], "as_of": AS_OF},
        doc,
        upsert=True
    )

    print(
        f"✅ Done: {meta['fund_key']} | "
        f"Holdings = {len(holdings)} | "
        f"Top-10 = {top_10_weight}"
    )
