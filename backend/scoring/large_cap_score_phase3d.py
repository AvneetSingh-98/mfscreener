import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

# =========================
# CATEGORY REGISTRY
# =========================
# Add new categories here ONLY
CATEGORIES = {
    "Large Cap": {
        "score_col": "score_large_cap",
        "cons_col": "score_large_cap_consistency",
        "rank_field": "large_cap"
    },
    "Flexi Cap": {
        "score_col": "score_flexi_cap",
        "cons_col": "score_flexi_cap_consistency",
        "rank_field": "flexi_cap"
    },
    "Mid Cap": {
        "score_col": "score_mid_cap",
        "cons_col": "score_mid_cap_consistency",
        "rank_field": "mid_cap"
    },
    "Small Cap": {
        "score_col": "score_small_cap",
        "cons_col": "score_small_cap_consistency",
        "rank_field": "small_cap"
    },
    "Multi Cap": {
        "score_col": "score_multi_cap",
        "cons_col": "score_multi_cap_consistency",
        "rank_field": "multi_cap"
    },
    "Value": {
        "score_col": "score_value_cap",
        "cons_col": "score_value_cap_consistency",
        "rank_field": "value_cap"
    },
    "ELSS": {
        "score_col": "score_elss_cap",
        "cons_col": "score_elss_cap_consistency",
        "rank_field": "elss_cap"
    },
    "Contra": {
        "score_col": "score_contra_cap",
        "cons_col": "score_contra_cap_consistency",
        "rank_field": "contra_cap"
    },
    "Focused": {
        "score_col": "score_focused_cap",
        "cons_col": "score_focused_cap_consistency",
        "rank_field": "focused_cap"
    },
    "Large & Mid Cap": {
    "score_col": "score_large_mid_cap",
    "cons_col": "score_large_mid_cap_consistency",
    "rank_field": "large_mid_cap"
}

}
# =========================
# DB CONNECTION
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

# =========================
# HELPERS
# =========================
def percentile(series, invert=False):
    """
    Percentile rank (NaN-safe)
    """
    p = series.rank(pct=True)
    return 1 - p if invert else p
def is_direct_growth(scheme_name: str) -> bool:
    name = scheme_name.lower()

    if "direct" not in name:
        return False

    # exclude IDCW / dividend / payout variants
    exclude_tokens = [
        "idcw",
        "dividend",
        "payout",
        "income distribution",
        "withdrawal"
    ]

    return not any(t in name for t in exclude_tokens)

# =========================
# MAIN RUNNER
# =========================
def run_phase_3d():

    for category, cfg in CATEGORIES.items():
        print(f"\n▶ Running Phase-3D for {category}")

        score_col = db[cfg["score_col"]]
        cons_col  = db[cfg["cons_col"]]
        rank_field = cfg["rank_field"]

        # =========================
        # LOAD RANK-ELIGIBLE SCHEMES
        # =========================
        raw_scores = list(score_col.find({
        "category": category,
        "metrics.performance": {"$exists": True},
        "metrics.risk": {"$exists": True},
        "metrics.risk_adjusted": {"$exists": True}
     }))

        scores = [
        s for s in raw_scores
        if is_direct_growth(s.get("scheme_name", ""))

        ]

        if not scores:
         print("⚠ No rank-eligible funds found")
         continue
     
        df = pd.json_normalize(scores)
        df["scheme_code"] = [s["scheme_code"] for s in scores]

        # =========================
        # LOAD CONSISTENCY (LEFT JOIN)
        # =========================
        cons = list(cons_col.find({"category": category}))
        df_cons = pd.json_normalize(cons)

        df = df.merge(df_cons, on="scheme_code", how="left")

        # =========================
        # CONSISTENCY (30%)
        # =========================
        df["cons_3y"] = percentile(df["consistency.rolling_3y.median"])
        df["cons_5y"] = percentile(df["consistency.rolling_5y.median"])

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
        # FINAL COMPOSITE SCORE
        # =========================
        df["quant_score"] = (
            30 * consistency_score +
            20 * risk_adj_score +
            25 * vol_score +
            25 * perf_score
        )

        # =========================
        # RANKING (NaN-SAFE)
        # =========================
        df["rank"] = np.nan
        rankable = df["quant_score"].notna()

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
                {"$set": {
                    "metrics.composite.quant_score": (
                        round(row["quant_score"], 2)
                        if pd.notna(row["quant_score"]) else None
                    ),
                    f"rank.{rank_field}": (
                        int(row["rank"]) if pd.notna(row["rank"]) else None
                    ),
                    "rank.universe_size": universe
                }}
            )

        print(f"✅ Phase-3D complete — {category}")
        print("Ranked funds:", universe)
        print("Unranked (insufficient data):", len(df) - universe)

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_phase_3d()
