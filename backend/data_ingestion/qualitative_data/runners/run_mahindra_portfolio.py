from pymongo import MongoClient
from extractors.mahindra_portfolio_excel import parse_mahindra_fund

# ============================
# CONFIG
# ============================

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-11\Mahindra Manulife\Mahindra_Portfolio.xlsx"

MAHINDRA_FUNDS = {
    "MM_LARGE_CAP": {
        "sheet": "MMF10",
        "category": "Large Cap"
    },
    "MM_LARGE_MID_CAP": {
        "sheet": "MMF14",
        "category": "Large & Mid Cap"
    },
    "MM_MID_CAP": {
        "sheet": "MMF07",
        "category": "Mid Cap"
    },
    "MM_SMALL_CAP": {
        "sheet": "MMF21",
        "category": "Small Cap"
    },
    "MM_FLEXI_CAP": {
        "sheet": "MMF18",
        "category": "Flexi Cap"
    },
    "MM_FOCUSED": {
        "sheet": "MMF16",
        "category": "Focused"
    },
    "MM_VALUE": {
        "sheet": "MMF25",
        "category": "Value"
    },
    "MM_ELSS": {
        "sheet": "MMF02",
        "category": "ELSS"
    },
    "MM_EQUITY_SAVINGS": {
        "sheet": "MMF03",
        "category": "Equity Savings"
    }
}

# ============================
# METRICS
# ============================

def compute_top_10_equity_weight(holdings):
    weights = [
        h["weight_num"]
        for h in holdings
        if h.get("section") == "equity"
        and isinstance(h.get("weight_num"), (int, float))
        and 0 < h["weight_num"] <= 30
    ]

    top_10 = round(sum(sorted(weights, reverse=True)[:10]), 2)

    if not (0 < top_10 <= 100):
        raise ValueError(f"Invalid Top-10 Equity Weight detected: {top_10}")

    return top_10

# ============================
# RUNNER
# ============================

if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017")
    db = client["mfscreener"]
    col = db["portfolio_holdings_v2"]

    for fund_key, meta in MAHINDRA_FUNDS.items():
        print("=" * 60)
        print(f"🚀 Running Mahindra fund : {fund_key}")

        holdings = parse_mahindra_fund(XLS_PATH, meta["sheet"])

        top_10_weight = compute_top_10_equity_weight(holdings)

        doc = {
            "fund_key": fund_key,
            "amc": "Mahindra Manulife Mutual Fund",
            "as_of": "2025-11-30",
            "asset_class": "Equity",
            "category": meta["category"],
            "holdings": holdings,
            "section_summary": {
                "equity": [h for h in holdings if h["section"] == "equity"],
                "cash": [h for h in holdings if h["section"] == "cash"]
            },
            "top_10_weight": top_10_weight
        }

        col.replace_one(
            {"fund_key": fund_key, "as_of": doc["as_of"]},
            doc,
            upsert=True
        )

        print(f"✅ Done: {fund_key} | Holdings = {len(holdings)} | Top-10 = {top_10_weight}")
