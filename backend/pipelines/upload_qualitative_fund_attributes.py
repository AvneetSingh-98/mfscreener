import os
from dotenv import load_dotenv
import certifi
import pandas as pd
from pymongo import MongoClient, ASCENDING
from datetime import datetime

load_dotenv()

# =========================
# CONFIG
# =========================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"
COLLECTION = "qualitative_fund_attributes"

EXCEL_PATH = r"D:\mfscreener-main\backend\pipelines\Factsheet_Fund_Key.xlsx"  # CHANGE THIS
SHEET_NAME = "Factsheet_Fund_Key"

# =========================
# DB SETUP
# =========================
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
col = db[COLLECTION]

col.create_index(
    [("fund_key", ASCENDING)],
    unique=True
)

# =========================
# HELPERS
# =========================
def safe_exp(x):
    try:
        return float(x)
    except:
        return None

def parse_managers(names, experiences):
    if pd.isna(names):
        return []

    name_list = [n.strip() for n in str(names).split(",")]
    exp_list = []

    if not pd.isna(experiences):
        exp_list = [e.strip() for e in str(experiences).split(",")]

    managers = []
    for i, name in enumerate(name_list):
        managers.append({
            "name": name,
            "experience_years": safe_exp(exp_list[i]) if i < len(exp_list) else None

        })

    return managers

# =========================
# MAIN INGEST
# =========================
def main():
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
    df.columns = [c.strip().lower() for c in df.columns]

    inserted = updated = 0

    for _, r in df.iterrows():
        fund_key = r["fund_key"]

        doc = {
            "fund_key": fund_key,
            "amc": r.get("amc"),
            "category": r.get("category"),
            "asset_class": r.get("asset_class"),

            "monthly_avg_aum_cr": r.get("monthly_avg_aum_cr"),
            "ter_direct_pct": r.get("ter_direct_pct"),
            "portfolio_turnover": r.get("portfolio_turnover"),

            "fund_manager": parse_managers(
                r.get("fund_manager"),
                r.get("fund_manager_experience")
            ),

            "notes": r.get("notes"),
            "source": "FACTSHEET_EXCEL",
            "updated_at": datetime.utcnow()
        }

        res = col.update_one(
            {"fund_key": fund_key},
            {"$set": doc},
            upsert=True
        )

        if res.upserted_id:
            inserted += 1
        else:
            updated += 1

    print("QUALITATIVE INGEST COMPLETE")
    print(f"Inserted: {inserted}")
    print(f"Updated : {updated}")

# =========================
if __name__ == "__main__":
    main()
