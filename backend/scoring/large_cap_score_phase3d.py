import numpy as np
import pandas as pd
from pymongo import MongoClient

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

score_col = db.score_large_cap
cons_col = db.score_large_cap_consistency

# =========================
# LOAD DATA
# =========================
scores = list(score_col.find({
    "metrics.performance": {"$exists": True},
    "metrics.risk": {"$exists": True},
    "metrics.risk_adjusted": {"$exists": True}
}))

if not scores:
    raise RuntimeError("No rank-eligible funds found")

df = pd.json_normalize(scores)
df["scheme_code"] = [s["scheme_code"] for s in scores]

# -------------------------
# LOAD CONSISTENCY METRICS
# -------------------------
cons = list(cons_col.find())
df_cons = pd.json_normalize(cons)

df = df.merge(df_cons, on="scheme_code", how="left")

# =========================
# HELPERS
# =========================
def percentile(series, invert=False):
    """Percentile rank, robust to NaNs"""
    p = series.rank(pct=True)
    return 1 - p if invert else p

# =========================
# CONSISTENCY (30%)
# =========================
df["cons_3y"] = percentile(df["consistency.rolling_3y.median"])
df["cons_5y"] = percentile(df["consistency.rolling_5y.median"])

# hit ratio proxy: above category P25
df["hit_ratio_raw"] = (
    df["consistency.rolling_3y.median"] >
    df["consistency.rolling_3y.p25"]
).astype(float)

df["hit_ratio"] = percentile(df["hit_ratio_raw"])

consistency_score = (
    0.12 * df["cons_3y"] +
    0.06 * df["cons_5y"] +
    0.12 * df["hit_ratio"]
)

# =========================
# RISK-ADJUSTED (20%)
# =========================
risk_adj_score = (
    0.08 * percentile(df["metrics.risk_adjusted.sharpe_3y"]) +
    0.06 * percentile(df["metrics.risk_adjusted.sortino_3y"]) +
    0.06 * percentile(df["metrics.risk_adjusted.information_ratio_3y"])
)

# =========================
# VOLATILITY & DRAWDOWN (25%)
# =========================
beta_penalty = 1 - abs(df["metrics.risk_adjusted.beta_3y"] - 1)

vol_score = (
    0.10 * percentile(df["metrics.risk.volatility"], invert=True) +
    0.10 * percentile(df["metrics.risk.max_drawdown"], invert=True) +
    0.05 * percentile(beta_penalty)
)

# =========================
# PERFORMANCE (25%)
# =========================
perf_score = (
    0.05 * percentile(df["metrics.performance.cagr_1y"]) +
    0.10 * percentile(df["metrics.performance.cagr_3y"]) +
    0.10 * percentile(df["metrics.performance.cagr_5y"])
)

# =========================
# FINAL QUANT SCORE
# =========================
df["quant_score"] = (
    30 * consistency_score +
    20 * risk_adj_score +
    25 * vol_score +
    25 * perf_score
)

# =========================
# RANKING (SAFE)
# =========================
rankable = df["quant_score"].notna()

df["rank"] = np.nan
df.loc[rankable, "rank"] = (
    df.loc[rankable, "quant_score"]
      .rank(ascending=False, method="min")
      .astype(int)
)

universe = int(rankable.sum())

# =========================
# WRITE BACK TO MONGO
# =========================
for _, row in df.iterrows():
    score_col.update_one(
        {"scheme_code": row["scheme_code"]},
        {
            "$set": {
                "metrics.composite": {
                    "quant_score": (
                        round(row["quant_score"], 2)
                        if pd.notna(row["quant_score"]) else None
                    ),
                    "bucket_scores": {
                        "consistency": (
                            round(consistency_score.loc[row.name] * 100, 2)
                            if pd.notna(consistency_score.loc[row.name]) else None
                        ),
                        "risk_adjusted": (
                            round(risk_adj_score.loc[row.name] * 100, 2)
                            if pd.notna(risk_adj_score.loc[row.name]) else None
                        ),
                        "volatility": (
                            round(vol_score.loc[row.name] * 100, 2)
                            if pd.notna(vol_score.loc[row.name]) else None
                        ),
                        "performance": (
                            round(perf_score.loc[row.name] * 100, 2)
                            if pd.notna(perf_score.loc[row.name]) else None
                        )
                    }
                },
                "rank.large_cap": (
                    int(row["rank"]) if pd.notna(row["rank"]) else None
                ),
                "rank.universe_size": universe
            }
        }
    )

print("✅ Phase 3D complete — Quantitative ranking generated")
print("Ranked funds:", universe)
print("Unranked (insufficient data):", len(df) - universe)
