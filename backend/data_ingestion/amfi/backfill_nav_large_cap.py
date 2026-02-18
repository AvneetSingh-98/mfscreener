import time
import requests
from datetime import datetime
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

# ---------- CONFIG ----------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")

MFAPI_URL = "https://api.mfapi.in/mf/{}"
RATE_LIMIT_SECONDS = 0.3

# ---------- DB ----------
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

funds_col = db.fund_master
nav_col = db.nav_history

nav_col.create_index(
    [("scheme_code", ASCENDING), ("date", ASCENDING)],
    unique=True
)


def backfill_nav_for_category(category):
    print(f"\n🔹 Starting NAV backfill for category: {category}")

    schemes = list(
        funds_col.find(
            {"category": category},
            {"scheme_code": 1, "_id": 0}
        )
    )

    print(f"✔ Found {len(schemes)} schemes")

    inserted = skipped = failed = 0

    for fund in schemes:
        scheme_code = fund["scheme_code"]
        url = MFAPI_URL.format(scheme_code)

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            nav_list = data.get("data", [])
            if not nav_list:
                continue

            for item in nav_list:
                try:
                    nav = float(item["nav"])
                    date = datetime.strptime(
                        item["date"], "%d-%m-%Y"
                    ).date().isoformat()
                except Exception:
                    continue

                try:
                    nav_col.insert_one({
                        "scheme_code": scheme_code,
                        "date": date,
                        "nav": nav,
                        "source": "MFAPI"
                    })
                    inserted += 1
                except Exception:
                    skipped += 1

            time.sleep(RATE_LIMIT_SECONDS)

        except Exception as e:
            failed += 1
            print(f"❌ {scheme_code} failed: {e}")

    print(f"✅ {category} backfill complete")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

EQUITY_CATEGORIES = [
   
    "Sectoral/ Thematic"
]

if __name__ == "__main__":
    for category in EQUITY_CATEGORIES:
        backfill_nav_for_category(category)


