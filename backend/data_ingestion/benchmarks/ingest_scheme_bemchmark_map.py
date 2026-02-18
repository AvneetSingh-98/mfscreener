import pandas as pd
from pymongo import MongoClient
import os
import re
from dotenv import load_dotenv
import certifi

load_dotenv()

# ---------------- CONFIG ----------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")
EXCEL_FILE = "Fund-Benchmark.xlsx"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

funds_col = db.fund_master
map_col = db.scheme_benchmark_map

# ---------------- HELPERS ----------------
def normalize_name(name: str) -> str:
    name = name.lower()

    # remove ONLY plan / option noise
    name = re.sub(
        r"(direct|regular|growth|plan|option|idcw|dividend|bonus|payout|withdrawal)",
        "",
        name,
    )

    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name)

    return name.strip()


# ---------------- LOAD FUND MASTER ----------------
fund_lookup = {}
for f in funds_col.find({}, {"scheme_code": 1, "scheme_name": 1}):
    fund_lookup[normalize_name(f["scheme_name"])] = f["scheme_code"]

print(f"Loaded {len(fund_lookup)} fund names from fund_master")

# ---------------- READ EXCEL ----------------
df = pd.read_excel(EXCEL_FILE, header=4)
df.columns = [str(c).strip() for c in df.columns]


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

    benchmark_raw = benchmark_raw.upper()

    if "NIFTY 500" in benchmark_raw:
        benchmark = "NIFTY_500"
    elif "BSE 500" in benchmark_raw:
        benchmark = "BSE_500"
    elif "NIFTY 100" in benchmark_raw:
        benchmark = "NIFTY_100"
    elif "BSE 100" in benchmark_raw:
        benchmark = "BSE_100"
    elif "NIFTY MIDCAP 150" in benchmark_raw:
        benchmark = "NIFTY_MIDCAP_150"
    elif "BSE MIDCAP 150" in benchmark_raw:
        benchmark = "BSE_MIDCAP_150"
    elif "NIFTY SMALLCAP 250" in benchmark_raw:
        benchmark="NIFTY_SMALLCAP_250"
    elif "BSE SMALLCAP 250" in benchmark_raw:
        benchmark = "BSE_SMALLCAP_250"
    elif "NIFTY MULTICAP 500" in benchmark_raw:
        benchmark = "NIFTY_MULTICAP_500"
    elif "BSE LARGEMIDCAP 250" in benchmark_raw:
        benchmark = "BSE_LARGEMIDCAP_250"
    elif "NIFTY LARGEMIDCAP 250" in benchmark_raw:
        benchmark = "NIFTY_LARGEMIDCAP_250"
    elif "NIFTY FINANCIAL SERVICES" in benchmark_raw:
        benchmark = "NIFTY_FINANCIAL_SERVICES"
    elif "NIFTY HEALTHCARE" in benchmark_raw:
        benchmark = "NIFTY_HEALTHCARE"
    elif "NIFTY IT" in benchmark_raw:
        benchmark = "NIFTY_IT"
    elif "ESG" in benchmark_raw and "100" in benchmark_raw:
        benchmark = "NIFTY_ESG_100"
    elif "NIFTY INDIA CONSUMPTION" in benchmark_raw:
        benchmark = "NIFTY_INDIA_CONSUMPTION"
    elif "NIFTY INFRASTRUCTURE" in benchmark_raw:
        benchmark = "NIFTY_INFRASTRUCTURE"
    elif "NIFTY 200" in benchmark_raw:
        benchmark = "NIFTY_200"
    else:
        continue


    map_col.update_one(
    { "scheme_code": scheme_code },
    {
        "$set": {
            "scheme_name": scheme_name,
            "benchmark": benchmark,
            "source": "CRISIL"
        }
    },
    upsert=True
)

    inserted += 1

print("✅ Scheme–benchmark mapping ingested")
print(f"Inserted: {inserted}")
print(f"Not matched: {not_found}")
print("Mongo count:", map_col.count_documents({}))
print("Sample:", map_col.find_one())
