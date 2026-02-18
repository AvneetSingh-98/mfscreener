# backend/pipelines/sector_and_portfolio_metrics.py

import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"
COLLECTION = "portfolio_holdings_v2"


def to_float(val):
    try:
        return float(val)
    except Exception:
        return 0.0


def compute_metrics(holdings):
    """
    Compute:
    - sector concentration (equity only)
    - number of equity stocks
    - top-10 equity weight
    """

    equity_holdings = [
        h for h in holdings
        if h.get("section") == "equity"
    ]

    sector_weights = defaultdict(float)

    for h in equity_holdings:
        sector = h.get("sector", "Unknown")
        weight = to_float(h.get("weight") or h.get("weight_num"))
        sector_weights[sector] += weight

    # round sector weights
    sector_concentration = {
        sector: round(wt, 2)
        for sector, wt in sector_weights.items()
        if wt > 0
    }

    equity_stock_count = len(equity_holdings)

    # Top-10 equity weight
    sorted_equity = sorted(
        equity_holdings,
        key=lambda x: to_float(x.get("weight") or x.get("weight_num")),
        reverse=True
    )

    top_10_equity_weight = round(
        sum(
            to_float(h.get("weight") or h.get("weight_num"))
            for h in sorted_equity[:10]
        ),
        2
    )

    return {
        "sector_concentration": sector_concentration,
        "equity_stock_count": equity_stock_count,
        "top_10_equity_weight": top_10_equity_weight,
    }


def main():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    col = db[COLLECTION]

    print("🚀 Computing sector + portfolio metrics...")

    updated = 0

    for doc in col.find():
        holdings = doc.get("holdings", [])
        if not holdings:
            continue

        metrics = compute_metrics(holdings)

        col.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "metrics": {
                        **metrics,
                        "updated_at": datetime.utcnow()
                    }
                }
            }
        )

        updated += 1

    print(f"✅ Updated {updated} funds with sector & portfolio metrics")


if __name__ == "__main__":
    main()
