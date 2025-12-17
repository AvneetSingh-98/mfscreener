import time
import requests
from datetime import datetime
from pymongo import MongoClient, ASCENDING
import os

# ---------- CONFIG ----------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "mfscreener")

MFAPI_URL = "https://api.mfapi.in/mf/{}"
RATE_LIMIT_SECONDS = 0.3  # be polite to API

# ---------- DB CONNECTION ----------
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

funds_col = db.fund_master
nav_col = db.nav_history

# Ensure uniqueness (safe if already exists)
nav_col.create_index(
    [("scheme_code", ASCENDING), ("date", ASCENDING)],
    unique=True
)


def backfill_large_cap_nav():
    print("🔹 Starting historical NAV backfill for Large Cap funds")

    large_cap_funds = list(
        funds_col.find(
            {"category": "Large Cap"},
            {"scheme_code": 1, "_id": 0}
        )
    )

    print(f"✔ Found {len(large_cap_funds)} Large Cap schemes")

    inserted = 0
    skipped = 0
    failed = 0

    for fund in large_cap_funds:
        scheme_code = fund["scheme_code"]
        url = MFAPI_URL.format(scheme_code)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            nav_list = data.get("data", [])
            if not nav_list:
                print(f"⚠ No NAV data for scheme {scheme_code}")
                continue

            for item in nav_list:
                try:
                    nav = float(item["nav"])
                    date = datetime.strptime(item["date"], "%d-%m-%Y").date().isoformat()
                except Exception:
                    continue

                doc = {
                    "scheme_code": scheme_code,
                    "date": date,
                    "nav": nav,
                    "source": "MFAPI"
                }

                try:
                    nav_col.insert_one(doc)
                    inserted += 1
                except Exception:
                    skipped += 1

            print(f"✔ Backfilled scheme {scheme_code}")

            time.sleep(RATE_LIMIT_SECONDS)

        except Exception as e:
            failed += 1
            print(f"❌ Failed scheme {scheme_code}: {e}")

    print("\n✅ Historical NAV backfill complete")
    print(f"Inserted: {inserted}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"Failed schemes: {failed}")


if __name__ == "__main__":
    backfill_large_cap_nav()
