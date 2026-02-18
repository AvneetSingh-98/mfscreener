import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

# --- SETUP ---
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

# Schemes to compare
schemes = {
    "118494": "Templeton India Value",
    "118481": "Bandhan (Working Code)"
}

RF_MONTHLY = 0.005 # 0.5%

def calculate_3y_sortino(code, name):
    print(f"\n--- Analysis for: {name} ({code}) ---")
    
    # 1. Fetch 3 YEARS of data (approx 1100 days)
    # Instead of .limit(40), we fetch everything and filter by date
    cursor = db.nav_history.find({"scheme_code": code}).sort("date", -1).limit(1100)
    df = pd.DataFrame(list(cursor))
    
    if df.empty:
        print("❌ No data found.")
        return

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 2. GROUP BY MONTH (Crucial for Monthly Sortino)
    df['month'] = df['date'].dt.to_period('M')
    monthly_df = df.groupby('month').last()
    
    # 3. Calculate Monthly Returns
    monthly_df['returns'] = monthly_df['nav'].pct_change().dropna()
    returns = monthly_df['returns'].dropna()
    
    print(f"Total Months Analyzed: {len(returns)}")
    print(f"Date Range: {monthly_df.index.min()} to {monthly_df.index.max()}")

    # 4. Sortino Math
    diffs = returns - RF_MONTHLY
    downside = np.minimum(diffs, 0)
    ds_deviation = np.sqrt((downside ** 2).mean())
    excess_return = returns.mean() - RF_MONTHLY
    
    if ds_deviation == 0:
        print("⚠️ ds is 0! Logic would return 99.")
        sortino = 99.0
    else:
        sortino = (excess_return / ds_deviation) * np.sqrt(12)
        print(f"Downside Deviation: {ds_deviation:.6f}")
        print(f"Final 3Y Sortino: {sortino:.2f}")

for code, name in schemes.items():
    calculate_3y_sortino(code, name)