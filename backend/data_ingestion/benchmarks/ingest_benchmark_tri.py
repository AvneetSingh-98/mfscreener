import pandas as pd
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

# =========================
# MONGO CONFIG
# =========================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
col = db.benchmark_nav

# unique constraint
col.create_index(
    [("benchmark", ASCENDING), ("date", ASCENDING)],
    unique=True
)

# =========================
# TRI INGESTION
# =========================
def ingest_tri(csv_path, benchmark_code):
    print(f"\n📥 Ingesting TRI → {benchmark_code}")
    print(f"File: {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    # ---- explicit column mapping (no guessing) ----
    REQUIRED_COLS = {"index_date", "tri"}
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in TRI CSV: {missing}")

    # parse & clean
    df["index_date"] = pd.to_datetime(
        df["index_date"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )
    df["tri"] = pd.to_numeric(df["tri"], errors="coerce")

    df = df.dropna(subset=["index_date", "tri"])

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            col.insert_one({
                "benchmark": benchmark_code,
                "date": row["index_date"],
                "nav": float(row["tri"]),
                "type": "TRI"   # 👈 optional but VERY useful later
            })
            inserted += 1
        except Exception:
            skipped += 1

    print(f"✅ Inserted : {inserted}")
    print(f"⏭️ Skipped  : {skipped} (duplicates)")
    print(f"📊 Total    : {inserted + skipped}")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    ingest_tri(
        "NIFTYFINANCIALSERVICESTRI.csv",
        "NIFTY_FINANCIAL_SERVICES_TRI"
    )
