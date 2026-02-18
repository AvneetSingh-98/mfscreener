import pandas as pd
import re
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

# =========================
# DB CONNECTION
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

fund_master_col = db["fund_master"]      # AMFI canonical
fund_master_v2  = db["fund_master_v2"]   # OUTPUT

# =========================
# LOAD AMC ALIASES
# =========================
print("📘 Loading factsheet Excel...")
factsheet = pd.read_excel("FACTSHEET_FULL_DATA.xlsx")

AMC_ALIASES = {}
for _, r in factsheet.iterrows():
    amc = str(r["amc"]).strip()
    fund_key = str(r["fund_key"])
    if "_" in fund_key:
        AMC_ALIASES[amc.lower()] = fund_key.split("_")[0]

print(f"✅ AMC aliases loaded: {len(AMC_ALIASES)}")

# =========================
# HELPERS
# =========================
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())

def is_index_fund(name: str) -> bool:
    n = name.lower()
    return any(x in n for x in [
        "index fund",
        "nifty",
        "sensex",
        "etf",
        "index"
    ])

def is_idcw_or_dividend(name: str) -> bool:
    n = name.lower()
    return any(x in n for x in [
        "idcw",
        "dividend",
        "payout",
        "bonus"
    ])

def resolve_category(doc) -> str | None:
    """
    Category resolution with correct precedence.
    """
    name = normalize(doc.get("scheme_name", ""))
    cat  = doc.get("category")
    sub  = doc.get("sub_category")

    # 1️⃣ ELSS (explicit + implicit)
    if (
        cat == "ELSS"
        or "tax saver" in name
        or "long term advantage" in name
    ):
        return "ELSS"

    # 2️⃣ Large & Mid Cap (AMFI sub_category OR name)
    if (
        sub == "Large & Mid Cap"
        or "large and mid cap" in name
        or "large & mid cap" in name
    ):
        return "Large & Mid Cap"

    # 3️⃣ Standard AMFI categories (trusted)
    if cat in {
        "Large Cap",
        "Mid Cap",
        "Small Cap",
        "Flexi Cap",
        "Focused",
        "Multi Cap",
        "Value",
        "Contra"
    }:
        return cat

    return None

# =========================
# PHASE-3 ELIGIBLE UNIVERSE
# =========================
ELIGIBLE_CATEGORIES = {
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Large & Mid Cap",
    "Flexi Cap",
    "Focused",
    "Multi Cap",
    "Value",
    "ELSS",
    "Contra"
}

# =========================
# BUILD fund_master_v2
# =========================
fund_master_v2.delete_many({})

mapped = 0
unmapped = []

cursor = fund_master_col.find({
    "category": {"$in": list(ELIGIBLE_CATEGORIES)},
    "scheme_name": {"$regex": "Direct", "$options": "i"}
})

schemes = list(cursor)
print(f"🔍 Eligible schemes for mapping: {len(schemes)}")

for doc in schemes:
    scheme_code = doc["scheme_code"]
    scheme_name = doc["scheme_name"]
    amc_name    = doc["amc"]

    # ❌ HARD EXCLUSIONS
    if is_index_fund(scheme_name):
        continue

    if is_idcw_or_dividend(scheme_name):
        continue

    category = resolve_category(doc)
    amc_key  = AMC_ALIASES.get(amc_name.lower())

    if not category or not amc_key:
        unmapped.append(scheme_name)
        continue

    fund_key = f"{amc_key}_{category.replace(' ', '_').upper()}"

    fund_master_v2.insert_one({
        "scheme_code": scheme_code,
        "scheme_name": scheme_name,
        "amc": amc_name,
        "category": category,
        "fund_key": fund_key,
        "created_at": datetime.utcnow()
    })

    mapped += 1

# =========================
# SUMMARY
# =========================
print("\n==========================")
print("📊 FUND MASTER V2 SUMMARY")
print("==========================")
print("Mapped schemes   :", mapped)
print("Unmapped schemes:", len(unmapped))

if unmapped:
    pd.DataFrame({"scheme_name": unmapped}).to_csv(
        "unmapped_fund_keys.csv", index=False
    )
    print("📝 Saved unmapped schemes to unmapped_fund_keys.csv")
