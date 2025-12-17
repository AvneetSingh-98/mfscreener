import numpy as np
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

nav_col = db["nav_history"]
fund_col = db["fund_master"]
score_col = db["score_large_cap"]

# =========================
# HELPERS
# =========================
def fetch_daily_nav(scheme_code):
    df = pd.DataFrame(
        list(nav_col.find(
            {"scheme_code": scheme_code},
            {"date": 1, "nav": 1, "_id": 0}
        ))
    )

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df.set_index("date")

    return df


def get_cagr_fixed_year_daily(df, years):
    """
    Groww-style CAGR:
    - Daily NAV
    - Fixed calendar lookback
    - NAV closest to (today - N years)
    """
    if df.empty:
        return None

    end_date = df.index.max()
    target_date = end_date - pd.DateOffset(years=years)

    df_start = df[df.index <= target_date]
    if df_start.empty:
        return None

    start_nav = df_start.iloc[-1]["nav"]
    end_nav = df.iloc[-1]["nav"]

    if start_nav <= 0 or end_nav <= 0:
        return None

    return (end_nav / start_nav) ** (1 / years) - 1


def max_drawdown(series):
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return drawdown.min()


# =========================
# MAIN RUNNER
# =========================
def run_phase_3a():
    schemes = fund_col.find({
        "category": "Large Cap",
        "$and": [
            {"scheme_name": {"$regex": "Direct", "$options": "i"}},
            {"scheme_name": {"$not": {"$regex": "Regular|IDCW|Dividend", "$options": "i"}}}
        ]
    })

    updated = 0
    skipped = 0

    for fund in schemes:
        scheme_code = fund["scheme_code"]

        df_daily = fetch_daily_nav(scheme_code)
        if df_daily is None or len(df_daily) < 250:
            skipped += 1
            continue

        # -------------------------
        # PERFORMANCE (DAILY CAGR)
        # -------------------------
        perf = {}

        for y in [1, 3, 5]:
            val = get_cagr_fixed_year_daily(df_daily, y)
            if val is not None:
                perf[f"cagr_{y}y"] = val

        # 3M / 6M absolute returns (daily)
        for m in [3, 6]:
            target_date = df_daily.index.max() - pd.DateOffset(months=m)
            df_start = df_daily[df_daily.index <= target_date]
            if not df_start.empty:
                start_nav = df_start.iloc[-1]["nav"]
                end_nav = df_daily.iloc[-1]["nav"]
                perf[f"return_{m}m"] = (end_nav / start_nav) - 1

        # -------------------------
        # RISK (MONTHLY FROM DAILY)
        # -------------------------
        df_monthly = df_daily.resample("M").last()
        returns = np.log(df_monthly["nav"] / df_monthly["nav"].shift(1)).dropna()

        risk = {
            "volatility": returns.std() * np.sqrt(12),
            "max_drawdown": max_drawdown(df_daily["nav"])
        }

        # -------------------------
        # WRITE
        # -------------------------
        score_col.update_one(
            {"scheme_code": scheme_code},
            {
                "$set": {
                    "scheme_name": fund["scheme_name"],
                    "category": fund["category"],
                    "metrics.performance": perf,
                    "metrics.risk": risk,
                    "meta": {
                        "cagr_method": "daily_fixed_calendar",
                        "risk_method": "monthly_log_from_daily",
                        "last_updated": datetime.utcnow()
                    }
                }
            },
            upsert=True
        )

        updated += 1

    print("✅ Phase 3A complete")
    print("Updated:", updated)
    print("Skipped:", skipped)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_phase_3a()
