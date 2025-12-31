import numpy as np
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# ======================
# DB CONNECTION
# ======================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

fund_col = db.fund_master
hold_col = db.portfolio_holdings
out_col = db.score_large_cap_phase4a

CATEGORY = "Large Cap"

# ======================
# LOAD DATA
# ======================
funds = list(fund_col.find({ "category": CATEGORY }))
holdings = list(hold_col.find())

if not holdings:
    raise RuntimeError("❌ No portfolio holdings found")

df_fund = pd.DataFrame(funds)
df_hold = pd.DataFrame(holdings)

df = df_fund.merge(df_hold, on="scheme_code", how="inner")

# ======================
# HELPER FUNCTIONS
# ======================
def bell_score(x, p25, med, p75):
    if x < p25:
        return 0.3 + 0.2 * (x / p25)
    elif p25 <= x < med:
        return 0.5 + 0.3 * ((x - p25) / (med - p25))
    elif med <= x <= p75:
        return 1.0
    else:
        return max(0.5, 1.0 - 0.5 * ((x - p75) / p75))

def percentile(series, invert=False):
    p = series.rank(pct=True)
    return 1 - p if invert else p

# ======================
# DERIVED METRICS
# ======================
df["stock_count"] = df["holdings"].apply(len)

df["top10_weight"] = df["holdings"].apply(
    lambda x: sum(sorted([h["weight"] for h in x], reverse=True)[:10])
)

def sector_hhi(holds):
    sector_sum = {}
    for h in holds:
        sector_sum[h["sector"]] = sector_sum.get(h["sector"], 0) + h["weight"]
    return sum((w / 100) ** 2 for w in sector_sum.values())

df["sector_concentration"] = df["holdings"].apply(sector_hhi)

# ======================
# CATEGORY STATS
# ======================
p25_sc, med_sc, p75_sc = np.percentile(df["stock_count"], [25, 50, 75])
p75_top10, p90_top10 = np.percentile(df["top10_weight"], [75, 90])
p75_sector, p90_sector = np.percentile(df["sector_concentration"], [75, 90])

# ======================
# SCORING
# ======================
df["stock_count_score"] = df["stock_count"].apply(
    lambda x: bell_score(x, p25_sc, med_sc, p75_sc)
)

def conc_score(x):
    if x <= p75_top10:
        return 1.0
    elif x <= p90_top10:
        return 1.0 - 0.5 * ((x - p75_top10) / (p90_top10 - p75_top10))
    else:
        return max(0.3, 0.5 - 0.5 * ((x - p90_top10) / p90_top10))

df["concentration_score"] = df["top10_weight"].apply(conc_score)

def sector_score(x):
    if x <= p75_sector:
        return 1.0
    elif x <= p90_sector:
        return 1.0 - 0.4 * ((x - p75_sector) / (p90_sector - p75_sector))
    else:
        return max(0.4, 0.6 - 0.6 * ((x - p90_sector) / p90_sector))

df["sector_score"] = df["sector_concentration"].apply(sector_score)

df["turnover_score"] = percentile(df["turnover_ratio"], invert=True)

# ======================
# FINAL PORTFOLIO QUALITY
# ======================
df["portfolio_quality_score"] = (
    0.25 * df["stock_count_score"] +
    0.25 * df["concentration_score"] +
    0.20 * df["sector_score"] +
    0.30 * df["turnover_score"]
)

# ======================
# WRITE TO MONGO
# ======================
out_col.delete_many({ "meta.category": CATEGORY })

for _, r in df.iterrows():
    out_col.insert_one({
        "scheme_code": r["scheme_code"],
        "portfolio_quality": {
            "stock_count_score": round(r["stock_count_score"], 3),
            "concentration_score": round(r["concentration_score"], 3),
            "sector_diversification_score": round(r["sector_score"], 3),
            "turnover_score": round(r["turnover_score"], 3)
        },
        "portfolio_quality_score": round(r["portfolio_quality_score"], 3),
        "meta": {
            "category": CATEGORY,
            "as_of": r.get("as_of"),
            "generated_at": datetime.utcnow()
        }
    })

print("✅ Phase 4A complete — Portfolio quality scores generated")
