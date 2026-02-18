from pymongo import MongoClient, ASCENDING
from fetch_nav import fetch_amfi_nav
from parse_nav import parse_amfi_nav
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

# --- CONFIG ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")


def store_nav_records():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    collection = db.nav_history

    # Ensure unique index
    collection.create_index(
        [("scheme_code", ASCENDING), ("date", ASCENDING)],
        unique=True
    )

    print("Fetching AMFI NAV data...")

    # SAFETY WRAPPER
    try:
        raw_text = fetch_amfi_nav()
    except Exception as e:
        print("AMFI NAV fetch failed. Skipping NAV ingestion for today.")
        print(e)
        return   # <--- prevents crash

    print("Parsing NAV records...")
    records = parse_amfi_nav(raw_text)

    if not records:
        print(" No NAV records parsed. Skipping insert.")
        return

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
            skipped += 1

    print(f"Inserted: {inserted}")
    print(f"Skipped (duplicates): {skipped}")
    print("NAV storage complete.")


if __name__ == "__main__":
    store_nav_records()
