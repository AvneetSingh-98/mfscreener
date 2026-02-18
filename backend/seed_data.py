import os
from dotenv import load_dotenv
import certifi
from datetime import datetime, timedelta
from pymongo import MongoClient
import random

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

funds_col = db.funds
scores_col = db.score_cache

# Clear existing data
funds_col.delete_many({})
scores_col.delete_many({})

funds = [
    {
        "fund_id": "ICICI_LC",
        "name": "ICICI Prudential Large Cap Fund",
        "show_name": "ICICI Prudential Large Cap",
        "amc": "ICICI Prudential",
        "category": "Large Cap",
        "benchmark": "NIFTY 100",
        "inception_date": datetime(2008, 1, 1),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "fund_id": "HDFC_LC",
        "name": "HDFC Large Cap Fund",
        "show_name": "HDFC Large Cap",
        "amc": "HDFC",
        "category": "Large Cap",
        "benchmark": "NIFTY 100",
        "inception_date": datetime(2007, 6, 1),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "fund_id": "SBI_LC",
        "name": "SBI Bluechip Fund",
        "show_name": "SBI Bluechip",
        "amc": "SBI",
        "category": "Large Cap",
        "benchmark": "NIFTY 100",
        "inception_date": datetime(2006, 2, 1),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]

funds_col.insert_many(funds)

scores = [
    {
        "fund_id": "ICICI_LC",
        "date": datetime.utcnow(),
        "final_score_default": 88.3,
        "bucket_scores": {
            "consistency": 32,
            "volatility": 17,
            "performance": 14,
            "portfolio_quality": 13,
            "valuation": 12,
        },
    },
    {
        "fund_id": "HDFC_LC",
        "date": datetime.utcnow(),
        "final_score_default": 86.1,
        "bucket_scores": {
            "consistency": 30,
            "volatility": 16,
            "performance": 15,
            "portfolio_quality": 14,
            "valuation": 11,
        },
    },
    {
        "fund_id": "SBI_LC",
        "date": datetime.utcnow(),
        "final_score_default": 84.7,
        "bucket_scores": {
            "consistency": 29,
            "volatility": 15,
            "performance": 14,
            "portfolio_quality": 13,
            "valuation": 13,
        },
    },
]

scores_col.insert_many(scores)

print("✅ Seeded Large Cap mutual fund data successfully")
