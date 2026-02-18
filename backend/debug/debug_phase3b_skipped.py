import pandas as pd
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
import numpy as np

# =========================
# DB
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

nav_col = db["nav_history"]
benchmark_col = db["benchmark_nav"]

# =========================
# CONFIG
# =========================
ROLLING_WINDOWS = {
    "3y": 36,
    "5y": 60
}

MIN_POINTS = {
    "3y": 20,
    "5y": 2
}

CATEGORY_CONFIG = {
    "Large Cap": "score_large_cap",
    "Flexi Cap": "score_flexi_cap",
    "Mid Cap": "score_mid_cap",
    "Small Cap": "score_small_cap",
    "Multi Cap": "score_multi_cap",
    "Value": "score_value_cap",
    "ELSS": "score_elss_cap",
    "Contra": "score_contra_cap",
    "Focused": "score_focused_cap",
    "Large & Mid Cap": "score_large_mid_cap",
    "Banking & Financial Services": "score_banking_financial_services",
    "Healthcare": "score_healthcare",
    "Infrastructure": "score_infrastructure",
    "Consumption": "score_consumption",
    "Business Cycle": "score_business_cycle",
    "ESG": "score_esg",
    "Technology": "score_technology",
    "Quant / Multi-Factor": "score_quant_multifactor"
}

# =========================
# HELPERS
# =========================
def fetch_monthly_nav(collection, key, value):
    df = pd.DataFrame(
        list(collection.find({key:value},{"date":1,"nav":1,"_id":0}))
    )
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month").last().reset_index()

# =========================
# MAIN
# =========================
def run():

    for cat, col_name in CATEGORY_CONFIG.items():

        col = db[col_name]

        cursor = col.find(
            {"phase3a_status":"eligible"},
            {"scheme_code":1,"scheme_name":1,"benchmark.code":1}
        )

        rows = []

        for f in cursor:

            code = f["scheme_code"]
            name = f["scheme_name"]
            benchmark = f.get("benchmark",{}).get("code")

            fund_df = fetch_monthly_nav(nav_col,"scheme_code",code)

            if fund_df is None or len(fund_df) < 36:
                rows.append([name,"NO_OR_INSUFFICIENT_FUND_NAV"])
                continue

            # ---------- rolling absolute ----------
            nav = fund_df["nav"]
            ok_abs = False

            for label, window in ROLLING_WINDOWS.items():
                values = []
                for i in range(window, len(nav)):
                    s = nav.iloc[i-window]
                    e = nav.iloc[i]
                    if s>0 and e>0:
                        values.append((e/s)**(1/(window/12))-1)

                if len(values) >= MIN_POINTS[label]:
                    ok_abs = True

            if not ok_abs:
                rows.append([name,"INSUFFICIENT_ROLLING_POINTS"])
                continue

            # ---------- alpha ----------
            if not benchmark:
                rows.append([name,"NO_BENCHMARK"])
                continue

            bench_df = fetch_monthly_nav(
                benchmark_col,"benchmark",benchmark
            )

            if bench_df is None:
                rows.append([name,"NO_BENCHMARK_NAV"])
                continue

            merged = fund_df.merge(
                bench_df,on="month"
            ).dropna()

            if len(merged) < 36:
                rows.append([name,"INSUFFICIENT_OVERLAP_WITH_BENCHMARK"])
                continue

        df = pd.DataFrame(rows,columns=["scheme_name","reason"])

        print(f"\n===== {cat} =====")
        print(df["reason"].value_counts())

        df.to_csv(f"phase3b_skipped_{cat.replace(' ','_')}.csv",index=False)

    print("\nCSV files written.")

if __name__ == "__main__":
    run()
