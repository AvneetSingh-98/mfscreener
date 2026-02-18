import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from collections import defaultdict
import json

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"
COLLECTION = "portfolio_holdings_v2"

FUND_KEY = "NIPPON_SMALL_CAP"
AS_OF = "2025-11-30"


def to_float(val):
    try:
        return float(val)
    except Exception:
        return 0.0


def is_equity(holding):
    # If section exists, enforce equity
    if "section" in holding:
        return holding.get("section") == "equity"
    # If section does not exist, assume equity (Nippon-style)
    return True


def main():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    col = db[COLLECTION]

    doc = col.find_one({
        "fund_key": FUND_KEY,
        "as_of": AS_OF
    })

    if not doc:
        print("❌ Fund not found")
        return

    sector_map = defaultdict(list)

    for h in doc.get("holdings", []):
        if not is_equity(h):
            continue

        sector = (h.get("sector") or "Unknown").lower()
        sector_map[sector].append({
            "company": h.get("company"),
            "isin": h.get("isin"),
            "weight": round(to_float(h.get("weight") or h.get("weight_num")), 2)
        })

    # Sort stocks within each sector by weight
    for sector in sector_map:
        sector_map[sector] = sorted(
            sector_map[sector],
            key=lambda x: x["weight"],
            reverse=True
        )

    output_path = "nippon_small_cap_sector_breakdown.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sector_map, f, indent=2)

    print(f"✅ Sector-wise stock breakdown written to {output_path}")
    print(f"📊 Sectors found: {len(sector_map)}")


if __name__ == "__main__":
    main()
