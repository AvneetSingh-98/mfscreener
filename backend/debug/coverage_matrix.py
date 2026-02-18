import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
import pandas as pd
import numpy as np

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

CATEGORIES = {
    "Large Cap": "normalized_large_cap_scores",
    "Mid Cap": "normalized_mid_cap_scores",
    "Small Cap": "normalized_small_cap_scores",
    "Large & Mid Cap": "normalized_large_&_mid_cap_scores",
    "Flexi Cap": "normalized_flexi_cap_scores",
    "Multi Cap": "normalized_multi_cap_scores",
    "Value": "normalized_value_scores",
    "ELSS": "normalized_elss_scores",
    "Contra": "normalized_contra_scores",
    "Focused": "normalized_focused_scores",
}

METRICS = {
    "returns": ["cagr_1y","cagr_3y","cagr_5y","return_3m","return_6m"],
    "consistency": ["rolling_3y","rolling_5y","iqr_3y","iqr_5y"],
    "risk": ["volatility","max_dd","up_beta","down_beta"],
    "risk_adjusted": ["sharpe","sortino","ir"],
    "portfolio_quality": [
        "stock_count","aum","top10","sector_hhi",
        "top3_sector","turnover","ter","manager_experience"
    ],
    "valuation": ["pe","pb","roe"]
}

rows = []

for category, coll in CATEGORIES.items():
    docs = list(db[coll].find({}))
    if not docs:
        continue

    for d in docs:
        amc = d.get("fund_key", "").split("_")[0]  # crude but works
        scores = d.get("normalized_sub_scores", {})

        for block, fields in METRICS.items():
            block_data = scores.get(block, {})
            for f in fields:
                val = block_data.get(f)
                rows.append({
                    "category": category,
                    "amc": amc,
                    "metric": f,
                    "available": val is not None
                })

df = pd.DataFrame(rows)

# -------- AGGREGATIONS --------

# Category × Metric
category_metric = (
    df.groupby(["category","metric"])["available"]
      .mean()
      .mul(100)
      .reset_index()
      .rename(columns={"available":"coverage_pct"})
)

# AMC × Metric
amc_metric = (
    df.groupby(["amc","metric"])["available"]
      .mean()
      .mul(100)
      .reset_index()
      .rename(columns={"available":"coverage_pct"})
)

# Category × AMC × Metric
category_amc_metric = (
    df.groupby(["category","amc","metric"])["available"]
      .mean()
      .mul(100)
      .reset_index()
      .rename(columns={"available":"coverage_pct"})
)

# -------- EXPORT --------
category_metric.to_csv("coverage_category_metric.csv", index=False)
amc_metric.to_csv("coverage_amc_metric.csv", index=False)
category_amc_metric.to_csv("coverage_category_amc_metric.csv", index=False)

print("✅ Coverage matrices generated:")
print(" - coverage_category_metric.csv")
print(" - coverage_amc_metric.csv")
print(" - coverage_category_amc_metric.csv")
