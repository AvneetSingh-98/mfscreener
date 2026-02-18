import os
import re
from datetime import datetime
from pymongo import MongoClient
from fetch_nav import fetch_amfi_nav
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]


def clean_scheme_code(raw_code: str):
    if not raw_code:
        return None
    cleaned = re.sub(r"[^\d]", "", raw_code)
    return cleaned if cleaned else None


def parse_category_header(line: str):
    """
    Example:
    Open Ended Schemes(Equity Scheme - Large Cap Fund)
    """

    category_raw = line.strip()

    clean = (
        line.replace("Open Ended Schemes", "")
        .replace("Close Ended Schemes", "")
        .strip("() ")
    )

    if "-" not in clean:
        return None, None, None, category_raw

    asset_part, sub_part = clean.split("-", 1)

    # Asset class normalization
    asset_part = asset_part.replace("Scheme", "").strip()
    if "Equity" in asset_part:
        asset_class = "Equity"
    elif "Debt" in asset_part:
        asset_class = "Debt"
    elif "Hybrid" in asset_part:
        asset_class = "Hybrid"
    elif "Solution" in asset_part:
        asset_class = "Solution Oriented"
    else:
        asset_class = "Other"

    sub_part = sub_part.replace("Fund", "").strip()

    # Category normalization (AMFI standard)
    if "Large Cap" in sub_part:
        category = "Large Cap"
    elif "Mid Cap" in sub_part:
        category = "Mid Cap"
    elif "Small Cap" in sub_part:
        category = "Small Cap"
    elif "Flexi Cap" in sub_part:
        category = "Flexi Cap"
    elif "Multi Cap" in sub_part:
        category = "Multi Cap"
    elif "Banking and PSU" in sub_part:
        category = "Banking & PSU"
    elif "Liquid" in sub_part:
        category = "Liquid"
    elif "Corporate Bond" in sub_part:
        category = "Corporate Bond"
    elif "ELSS" in sub_part:
        category = "ELSS"
    else:
        category = sub_part

    return asset_class, category, sub_part, category_raw


def build_fund_master():
    print("🔹 Building Fund Master from AMFI NAV data...")

    lines = fetch_amfi_nav()

    current_asset_class = None
    current_category = None
    current_sub_category = None
    current_category_raw = None
    current_amc = None

    processed = 0
    unknown_category = 0
    raw_scheme_lines = 0

    # CLEAN REBUILD
    db.fund_master.delete_many({})

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # CATEGORY HEADER
        if "Schemes(" in line or "Schemes (" in line:
            (
                current_asset_class,
                current_category,
                current_sub_category,
                current_category_raw,
            ) = parse_category_header(line)
            continue

        # AMC HEADER
        if line.endswith("Mutual Fund"):
            current_amc = line
            continue

        # COLUMN HEADER
        if line.startswith("Scheme Code"):
            continue

        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 4:
            continue

        raw_scheme_lines += 1

        scheme_code = clean_scheme_code(parts[0])
        scheme_name = parts[3]

        if not scheme_code:
            continue

        if not current_category:
            unknown_category += 1

        doc = {
            "scheme_code": scheme_code,
            "scheme_name": scheme_name,
            "amc": current_amc,
            "category_raw": current_category_raw,
            "asset_class": current_asset_class,
            "category": current_category,
            "sub_category": current_sub_category,
            "source": "AMFI",
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        db.fund_master.update_one(
            {"scheme_code": scheme_code},
            {"$set": doc},
            upsert=True
        )

        processed += 1

    print("✅ Fund Master Build Complete")
    print(f"✔ Raw scheme lines seen: {raw_scheme_lines}")
    print(f"✔ Schemes processed: {processed}")
    print(f"⚠ Unknown categories: {unknown_category}")


if __name__ == "__main__":
    build_fund_master()
