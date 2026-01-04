from pymongo import MongoClient
from datetime import datetime
from extractors.mirae_sheet_resolver import resolve_mirae_sheet
from extractors.mirae_portfolio_excel import parse_mirae_portfolio

# =====================
# CONFIG
# =====================
XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-11\Mirae Asset\Mirae_Portfolio.xlsx"
AS_OF = "2025-11-30"

FUNDS = [
    {
        "fund_key": "MIRAE_INNOVATION_OPP",
        "sheet": "Innovation Opportunities",
        "category": "Large Cap",
    },
    {
        "fund_key": "MIRAE_EQUITY_BLUECHIP",
        "sheet": "Equity Bluechip",
        "category": "Large & Mid Cap",
    },
    {
        "fund_key": "MIRAE_FLEXI_CAP",
        "sheet": "Flexi Cap",
        "category": "Flexi Cap",
    },
    {
        "fund_key": "MIRAE_MID_CAP",
        "sheet": "Mid Cap",
        "category": "Mid Cap",
    },
    {
        "fund_key": "MIRAE_FOCUSED",
        "sheet": "Focused",
        "category": "Focused",
    },
]

# =====================
# DB
# =====================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

# =====================
# TOP 10 (LOCKED & CORRECT)
# =====================
def compute_top_10_equity_weight(holdings):
    weights = [h["weight_num"] for h in holdings if h["section"] == "equity"]

    if not weights:
        return 0.0

    # Mirae uses fractional values (0–1)
    if max(weights) <= 1:
        weights = [w * 100 for w in weights]

    top_10 = round(sum(sorted(weights, reverse=True)[:10]), 2)

    if not (0 < top_10 <= 100):
        raise ValueError(f"❌ Invalid Top-10 Equity Weight: {top_10}")

    return top_10

# =====================
# RUN
# =====================
for meta in FUNDS:
    print("=" * 60)
    print(f"🚀 Running Mirae fund : {meta['fund_key']}")

    sheet = resolve_mirae_sheet(XLS_PATH, meta["sheet"])
    print(f"📄 Sheet used : {sheet}")

    holdings = parse_mirae_portfolio(XLS_PATH, sheet)
    top_10_weight = compute_top_10_equity_weight(holdings)

    doc = {
        "fund_key": meta["fund_key"],
        "amc": "Mirae Asset Mutual Fund",
        "as_of": AS_OF,
        "asset_class": "Equity",
        "category": meta["category"],
        "holdings": holdings,
        "counts": {
            "equity": len(holdings)
        },
        "section_summary": {
            "equity": round(sum(h["weight_num"] for h in holdings) * 100, 2),
        },
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
