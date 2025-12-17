from pymongo import MongoClient, ASCENDING
from fetch_nav import fetch_amfi_nav
from parse_nav import parse_amfi_nav
import os

# --- CONFIG ---
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "mfscreener")


def store_nav_records():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db.nav_history

    # Ensure unique index (safe to run multiple times)
    collection.create_index(
        [("scheme_code", ASCENDING), ("date", ASCENDING)],
        unique=True
    )

    print("Fetching AMFI NAV data...")
    raw_text = fetch_amfi_nav()

    print("Parsing NAV records...")
    records = parse_amfi_nav(raw_text)

    print(f"Inserting {len(records)} NAV records...")

    inserted = 0
    skipped = 0

    for record in records:
        doc = {
            "scheme_code": record["scheme_code"],
            "date": record["date"],
            "nav": record["nav"],
            "source": "AMFI"
        }

        try:
            collection.insert_one(doc)
            inserted += 1
        except Exception:
            # Duplicate (already exists)
            skipped += 1

    print(f"Inserted: {inserted}")
    print(f"Skipped (duplicates): {skipped}")
    print("NAV storage complete.")


if __name__ == "__main__":
    store_nav_records()
