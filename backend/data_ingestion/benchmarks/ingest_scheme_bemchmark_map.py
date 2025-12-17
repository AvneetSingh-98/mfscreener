import pandas as pd
from pymongo import MongoClient
import os
import re

# ---------------- CONFIG ----------------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "mfscreener")
EXCEL_FILE = "Fund-Benchmark.xlsx"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

funds_col = db.fund_master
map_col = db.scheme_benchmark_map

map_col.delete_many({})

# ---------------- HELPERS ----------------
def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"direct|regular|growth|plan|option", "", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# ---------------- LOAD FUND MASTER ----------------
fund_lookup = {}
for f in funds_col.find({}, {"scheme_code": 1, "scheme_name": 1}):
    fund_lookup[normalize_name(f["scheme_name"])] = f["scheme_code"]

print(f"Loaded {len(fund_lookup)} fund names from fund_master")

# ---------------- READ EXCEL ----------------
df = pd.read_excel(EXCEL_FILE, header=4)
df.columns = [c.strip() for c in df.columns]

print("Detected columns:", list(df.columns))

required = {"Scheme Name", "Benchmark"}
if not required.issubset(df.columns):
    raise ValueError("❌ Required columns missing")

inserted = 0
not_found = 0

# ---------------- INGEST ----------------
for _, row in df.iterrows():
    scheme_name = str(row["Scheme Name"]).strip()
    benchmark_raw = str(row["Benchmark"]).upper()

    if not scheme_name or scheme_name == "nan":
        continue

    key = normalize_name(scheme_name)

    scheme_code = fund_lookup.get(key)
    if not scheme_code:
        not_found += 1
        continue

    if "NIFTY" in benchmark_raw:
        benchmark = "NIFTY_100"
    elif "BSE" in benchmark_raw:
        benchmark = "BSE_100"
    else:
        continue

    map_col.insert_one({
        "scheme_code": scheme_code,
        "scheme_name": scheme_name,
        "benchmark": benchmark,
        "source": "CRISIL"
    })
    inserted += 1

print("✅ Scheme–benchmark mapping ingested")
print(f"Inserted: {inserted}")
print(f"Not matched: {not_found}")
print("Mongo count:", map_col.count_documents({}))
print("Sample:", map_col.find_one())
