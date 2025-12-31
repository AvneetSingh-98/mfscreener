import pandas as pd
from pymongo import MongoClient, ASCENDING
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "mfscreener")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
col = db.benchmark_nav

col.create_index(
    [("benchmark", ASCENDING), ("date", ASCENDING)],
    unique=True
)

def detect_date_col(columns):
    for c in columns:
        if "date" in c.lower():
            return c
    raise ValueError("No date column found")

def detect_value_col(columns):
    for c in columns:
        if "close" in c.lower() or "index" in c.lower():
            return c
    raise ValueError("No index value column found")

def ingest(csv_path, benchmark_code):
    print(f"Ingesting {benchmark_code} from {csv_path}")

    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]

    print("Detected columns:", list(df.columns))

    date_col = detect_date_col(df.columns)
    value_col = detect_value_col(df.columns)

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    df = df.dropna(subset=[date_col, value_col])

    inserted = 0
    for _, row in df.iterrows():
        try:
            col.insert_one({
                "benchmark": benchmark_code,
                "date": row[date_col],
                "nav": float(row[value_col])
            })
            inserted += 1
        except:
            pass

    print(f"✅ {benchmark_code}: inserted {inserted}")

if __name__ == "__main__":
    ingest("NIFTY100.csv", "NIFTY_100")
    ingest("BSE100.csv", "BSE_100")
    ingest("NIFTY500.csv", "NIFTY_500")
    ingest("BSE500.csv", "BSE_500")
    ingest("NIFTYMIDCAP150.csv","NIFTY_MIDCAP_150")
    ingest("BSEMIDCAP150.csv","BSE_MIDCAP_150")
    ingest("BSESMALLCAP250.CSV","BSE_SMALLCAP_250")
    ingest("NIFTYSMALLCAP250.CSV","NIFTY_SMALLCAP_250")
    ingest("NIFTY500MULTICAP.csv","NIFTY_MULTICAP_500")