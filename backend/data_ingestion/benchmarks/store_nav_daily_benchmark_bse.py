# BSE DAILY INDEX NAV — USES NSE TRADE DATE (NO SCRAPING)

import os
import requests
import pandas as pd
from pymongo import MongoClient, ASCENDING
from datetime import timedelta
from dotenv import load_dotenv
import certifi

load_dotenv()

MAX_BSE_LOOKBACK = 3 # days

# =========================
# CONFIG
# =========================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"

BENCHMARK_COL = "benchmark_nav"
META_COL = "meta_trade_dates"

BASE_DIR = os.path.dirname(__file__)
BSE_DIR = os.path.join(BASE_DIR, "bse_daily")
os.makedirs(BSE_DIR, exist_ok=True)

# ONLY REQUIRED INDICES
BSE_INDEX_MAP = {
    "BSE100":  "BSE_100",
    "BSE500":  "BSE_500",
    "MID150":  "BSE_MIDCAP_150",
    "SML250":  "BSE_SMALLCAP_250",
    "LMI250":  "BSE_LARGEMIDCAP_250",
}

# =========================
# DB
# =========================
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

bench_col = db[BENCHMARK_COL]
meta_col = db[META_COL]

bench_col.create_index(
    [("benchmark", ASCENDING), ("date", ASCENDING)],
    unique=True
)
def ingest_bse_csv(csv_path, trade_date):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    inserted = skipped = 0

    for _, row in df.iterrows():
        index_id = str(row["IndexID"]).strip()

        if index_id not in BSE_INDEX_MAP:
            continue

        try:
            col.insert_one({
                "benchmark": BSE_INDEX_MAP[index_id],
                "date": trade_date,
                "nav": float(row["ClosePrice"]),
                "source": "BSE_INDEX_SUMMARY"
            })
            inserted += 1
        except:
            skipped += 1

    print(f"BSE : Inserted: {inserted}, Skipped: {skipped}")

def main():
    meta = meta_col.find_one({"source": "NSE"})
    if not meta:
        print("NSE trade date missing — aborting BSE")
        return

    base_date = meta["date"]

    for i in range(0, MAX_BSE_LOOKBACK + 1):
        trade_date = base_date - timedelta(days=i)
        date_str = trade_date.strftime("%d%m%Y")

        url = f"https://www.bseindia.com/bsedata/Index_Bhavcopy/INDEXSummary_{date_str}.csv"
        file_path = os.path.join(BSE_DIR, f"INDEXSummary_{date_str}.csv")

        print(f"Trying BSE Index Summary: {url}")
        r = requests.get(url, timeout=30)

        if r.status_code != 200:
            continue   # 🔑 continue ONLY makes sense inside loop

        with open(file_path, "wb") as f:
            f.write(r.content)

        print(f"BSE CSV found for {trade_date}")
        ingest_bse_csv(file_path, trade_date)
        return   # 🔑 exit main() once success

    # 🔴 THIS must run ONLY if loop never succeeded
    print(" BSE CSV not available within allowed lookback")


# =========================
# MAIN
# =========================


if __name__ == "__main__":
    main()
