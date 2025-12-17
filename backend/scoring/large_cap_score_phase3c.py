import numpy as np
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# =========================
# CONFIG
# =========================
LOOKBACK_MONTHS = 36
MIN_MONTHS = 30
RISK_FREE_RATE = 0.06
RF_MONTHLY = RISK_FREE_RATE / 12

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

nav_col = db["nav_history"]
benchmark_col = db["benchmark_nav"]
map_col = db["scheme_benchmark_map"]
score_col = db["score_large_cap"]

# =========================
# HELPERS
# =========================
def fetch_monthly_nav(collection, key, value):
    df = pd.DataFrame(
        list(collection.find(
            {key: value},
            {"date": 1, "nav": 1, "_id": 0}
        ))
    )
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    df["month"] = df["date"].dt.to_period("M")
    df = df.groupby("month").last().reset_index()

    return df.tail(LOOKBACK_MONTHS)


def log_returns(df):
    df["ret"] = np.log(df["nav"] / df["nav"].shift(1))
    return df.dropna()


# =========================
# METRICS
# =========================
def sharpe_ratio(r):
    std = r.std()
    return None if std == 0 else ((r.mean() - RF_MONTHLY) / std) * np.sqrt(12)


def sortino_ratio(r):
    downside = r[r < RF_MONTHLY]
    if downside.empty:
        return None
    d_std = np.sqrt(((downside - RF_MONTHLY) ** 2).mean())
    return None if d_std == 0 else ((r.mean() - RF_MONTHLY) / d_std) * np.sqrt(12)


def beta(rs, rb):
    var_b = np.var(rb)
    return None if var_b == 0 else np.cov(rs, rb)[0][1] / var_b


def information_ratio(rs, rb):
    active = rs - rb
    std = active.std()
    return None if std == 0 else (active.mean() / std) * np.sqrt(12)


# =========================
# MAIN RUNNER
# =========================
def run_phase_3c():
    updated = 0
    skipped = 0

    for row in map_col.find({}):
        scheme_code = row["scheme_code"]
        benchmark_code = row["benchmark"]

        scheme_nav = fetch_monthly_nav(nav_col, "scheme_code", scheme_code)
        bench_nav = fetch_monthly_nav(benchmark_col, "benchmark", benchmark_code)

        if scheme_nav is None or bench_nav is None:
            skipped += 1
            continue

        scheme_ret = log_returns(scheme_nav)
        bench_ret = log_returns(bench_nav)

        merged = scheme_ret.merge(
            bench_ret,
            on="month",
            suffixes=("_s", "_b")
        )

        if len(merged) < MIN_MONTHS:
            skipped += 1
            continue

        rs = merged["ret_s"]
        rb = merged["ret_b"]

        metrics = {
            "sharpe_3y": round(sharpe_ratio(rs), 4) if sharpe_ratio(rs) is not None else None,
            "sortino_3y": round(sortino_ratio(rs), 4) if sortino_ratio(rs) is not None else None,
            "information_ratio_3y": round(information_ratio(rs, rb), 4) if information_ratio(rs, rb) is not None else None,
            "beta_3y": round(beta(rs, rb), 4) if beta(rs, rb) is not None else None
        }

        score_col.update_one(
            { "scheme_code": scheme_code },
            {
                "$set": {
                    "metrics.risk_adjusted": metrics,
                    "benchmark.code": benchmark_code,
                    "meta.last_updated": datetime.utcnow()
                }
            },
            upsert=True
        )

        updated += 1

    print("✅ Phase 3C complete")
    print("Updated:", updated)
    print("Skipped:", skipped)


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_phase_3c()

