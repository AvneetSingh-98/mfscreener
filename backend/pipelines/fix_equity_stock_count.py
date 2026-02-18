import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"
COLLECTION = "portfolio_holdings_v2"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
col = db[COLLECTION]


def compute_equity_stock_count(doc):
    """
    Correct equity stock count across all AMC formats
    PRIORITY:
    1. segregation_summary / section_summary
    2. holdings.asset_class
    3. fallback (rare)
    """

    # ---------- PRIORITY 1: Section / Segregation ----------
    section = doc.get("segregation_summary") or doc.get("section_summary")

    if isinstance(section, dict):
        equity_cnt = 0

        equity = section.get("equity")
        equity_foreign = section.get("equity_foreign")

        if isinstance(equity, list):
            equity_cnt += len(equity)

        if isinstance(equity_foreign, list):
            equity_cnt += len(equity_foreign)

        if equity_cnt > 0:
            return equity_cnt

    # ---------- PRIORITY 2: Holdings with asset_class ----------
    holdings = doc.get("holdings")

    if isinstance(holdings, list) and len(holdings) > 0:
        equity = [
            h for h in holdings
            if str(h.get("asset_class", "")).lower() == "equity"
        ]

        if equity:
            return len(equity)

    # ---------- LAST FALLBACK ----------
    return None



def main():
    updated = skipped = 0

    for doc in col.find(
        {"as_of": "2025-12-31"},
        {
            "_id": 1,
            "holdings": 1,
            "section_summary": 1,
            "segregation_summary": 1
        }
    ):
        count = compute_equity_stock_count(doc)

        if count is None:
            skipped += 1
            continue

        res = col.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "metrics.equity_stock_count": count,
                    "metrics.equity_stock_count_updated_at": datetime.utcnow()
                }
            }
        )

        if res.modified_count:
            updated += 1
        else:
            skipped += 1

    print("Equity stock count fix completed")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")


if __name__ == "__main__":
    main()
