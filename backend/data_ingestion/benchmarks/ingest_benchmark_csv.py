import pandas as pd
from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mfscreener")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]
col = db.benchmark_nav

col.create_index(
    [("benchmark", ASCENDING), ("date", ASCENDING)],
    unique=True
)
def load_file(path):
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        try:
            return pd.read_csv(path, encoding="utf-8")
        except:
            return pd.read_csv(path, encoding="latin1", engine="python", on_bad_lines="skip")

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

    df = load_file(csv_path)
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

    print(f"{benchmark_code}: inserted {inserted}")

if __name__ == "__main__":
    
    ingest("NIFTY200.xlsx","NIFTY_200")
    ingest("NIFTYFINANCIALSERVICES.csv","NIFTY_FINANCIAL_SERVICES")
    ingest("NIFTYHEALTHCARE.xlsx","NIFTY_HEALTHCARE")
    ingest("NIFTYINDIACONSUMPTION.xlsx","NIFTY_INDIA_CONSUMPTION")
    ingest("NIFTYINFRASTRUCTURE.xlsx","NIFTY_INFRASTRUCTURE")
    ingest("NIFTYIT.xlsx","NIFTY_IT")
    ingest("NIFTY100ESG.xlsx","NIFTY_ESG_100")