# NSE DAILY EOD — AUTHORITATIVE TRADE DATE
# Stores benchmark NAVs + locks NSE trade date for downstream use

import os
from dotenv import load_dotenv
import certifi
import io
import requests
import pandas as pd
from datetime import date, timedelta
from pymongo import MongoClient, ASCENDING

load_dotenv()

# =========================
# CONFIG
# =========================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"

BENCHMARK_COL = "benchmark_nav"
META_COL = "meta_trade_dates"

URL_TPL = "https://www.niftyindices.com/Daily_Snapshot/ind_close_all_{ddmmyyyy}.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 20
MAX_LOOKBACK_DAYS = 5

# =========================
# NSE TARGETS
# =========================
NSE_TARGETS = {
    "NIFTY 100": "NIFTY_100",
    "NIFTY 200": "NIFTY_200",
    "NIFTY 500": "NIFTY_500",

    "NIFTY MIDCAP 150": "NIFTY_MIDCAP_150",
    "NIFTY SMALLCAP 250": "NIFTY_SMALLCAP_250",

    "NIFTY500 MULTICAP 50:25:25": "NIFTY_MULTICAP_500",
    "NIFTY LARGEMIDCAP 250": "NIFTY_LARGEMIDCAP_250",

    "NIFTY FINANCIAL SERVICES": "NIFTY_FINANCIAL_SERVICES",
    "NIFTY HEALTHCARE INDEX": "NIFTY_HEALTHCARE",
    "NIFTY IT": "NIFTY_IT",
    "NIFTY INDIA CONSUMPTION": "NIFTY_INDIA_CONSUMPTION",
    "NIFTY INFRASTRUCTURE": "NIFTY_INFRASTRUCTURE",
    "NIFTY100 ESG": "NIFTY_ESG_100"
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

meta_col.create_index(
    [("source", ASCENDING)],
    unique=True
)

# =========================
# CSV PARSING
# =========================
def find_header_start(txt):
    lines = txt.splitlines()
    for i, line in enumerate(lines):
        if "Index Name" in line and "Index Date" in line:
            return sum(len(x) + 1 for x in lines[:i])
    return -1

def parse_csv(text):
    start = find_header_start(text)
    if start == -1:
        return None
    return pd.read_csv(io.StringIO(text[start:]), engine="python")

# =========================
# FETCH NSE (LOOKBACK SAFE)
# =========================
def fetch_latest_nse():
    for i in range(1, MAX_LOOKBACK_DAYS + 1):
        d = date.today() - timedelta(days=i)
        url = URL_TPL.format(ddmmyyyy=d.strftime("%d%m%Y"))

        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code != 200 or not r.text.strip():
                continue

            df = parse_csv(r.text)
            if df is not None and not df.empty:
                print(f"NSE EOD found for {d}")
                return df, d
        except:
            pass

    return None, None

# =========================
# INGEST NSE
# =========================
def ingest_nse(df):
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df["index_date"] = pd.to_datetime(
        df["index_date"], errors="coerce", dayfirst=True
    ).dt.normalize()

    inserted = skipped = 0

    for _, r in df.iterrows():
        name = str(r["index_name"]).strip().upper()

        matched = None
        for prefix, code in NSE_TARGETS.items():
            if name == prefix:   # exact match only
                matched = code
                break

        if not matched:
            continue

        try:
            bench_col.insert_one({
                "benchmark": matched,
                "date": r["index_date"],
                "nav": float(r["closing_index_value"]),
                "source": "NSE_EOD"
            })
            inserted += 1
        except:
            skipped += 1

    print(f"NSE : Inserted: {inserted}, Skipped: {skipped}")

# =========================
# MAIN
# =========================
def main():
    df, trade_date = fetch_latest_nse()
    if df is None:
        print("No NSE EOD file found")
        return

    ingest_nse(df)

    # 🔒 LOCK NSE TRADE DATE
    meta_col.update_one(
        {"source": "NSE"},
        {
            "$set": {
                "date": pd.to_datetime(trade_date),
                "updated_at": pd.Timestamp.utcnow()
            }
        },
        upsert=True
    )

    print(f"NSE trade date locked: {trade_date}")

if __name__ == "__main__":
    main()

