import pandas as pd
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
import re

# =========================
# DB
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

nav_col = db["nav_history"]
benchmark_col = db["benchmark_nav"]
fund_map_col = db["fund_benchmark_map"]

# =========================
# CONFIG
# =========================
LOOKBACK_MONTHS = 36
MIN_MONTHS = 30

SCORE_COLLECTIONS = [
    "score_banking_financial_services",
    "score_healthcare",
    "score_infrastructure",
    "score_consumption",
    "score_business_cycle",
    "score_esg",
    "score_technology",
    "score_quant_multifactor"
]

# =========================
# HELPERS
# =========================
def canon(name):
    name = name.lower()
    for t in ["direct","regular","growth","plan","option","fund","idcw","dividend"]:
        name = name.replace(t,"")
    name = re.sub(r"[^a-z0-9 ]+"," ",name)
    return " ".join(name.split())

def fetch_monthly_nav(col, key, val):
    df = pd.DataFrame(list(col.find({key: val},{"date":1,"nav":1,"_id":0})))
    if df.empty:
        return None
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month").last().reset_index()

# =========================
# BUILD FUND MAP
# =========================
fund_map = {}
for r in fund_map_col.find({}):
    k = canon(r["fund_key"])
    if k not in fund_map:
        fund_map[k] = r["benchmark"]

# =========================
# MAIN
# =========================
def run():

    summary = {}

    for col_name in SCORE_COLLECTIONS:
        col = db[col_name]
        skipped = col.find({
            "metrics.performance": {"$exists": True},
            "metrics.risk_adjusted": {"$exists": False}
        })

        rows = []

        for f in skipped:
            code = f["scheme_code"]
            name = f["scheme_name"]
            key = canon(name)

            # ---------- benchmark ----------
            benchmark = fund_map.get(key)

            if not benchmark:
                rows.append([name,"NO_BENCHMARK",None])
                continue

            fund_nav = fetch_monthly_nav(nav_col,"scheme_code",code)
            bench_nav = fetch_monthly_nav(benchmark_col,"benchmark",benchmark)

            if fund_nav is None:
                rows.append([name,"NO_FUND_NAV",benchmark])
                continue

            if bench_nav is None:
                rows.append([name,"NO_BENCHMARK_NAV",benchmark])
                continue

            merged = fund_nav.merge(bench_nav,on="month").dropna()

            if len(merged) < MIN_MONTHS:
                rows.append([name,f"LESS_THAN_{MIN_MONTHS}_MONTHS",benchmark])
                continue

            rows.append([name,"UNKNOWN",benchmark])

        df = pd.DataFrame(rows,columns=["scheme_name","reason","benchmark"])
        summary[col_name] = df

        print(f"\n===== {col_name} =====")
        print(df["reason"].value_counts())

        df.to_csv(f"skipped_{col_name}.csv",index=False)

    print("\nCSV files written for each category.")

if __name__ == "__main__":
    run()
