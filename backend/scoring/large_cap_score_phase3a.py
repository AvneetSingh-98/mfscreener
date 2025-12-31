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

# =========================
# CATEGORY CONFIG
# =========================
CATEGORY_CONFIG = {
    "Large Cap": {
        "score_collection": "score_large_cap"
    },
    "Flexi Cap": {
        "score_collection": "score_flexi_cap"
    },
    "Mid Cap": {
        "score_collection": "score_mid_cap"
    },
    "Small Cap": {
        "score_collection": "score_small_cap"
    },
    "Multi Cap": {
        "score_collection": "score_multi_cap"
    },
    "Value": {
        "score_collection": "score_value_cap"
    },
    "ELSS": {
        "score_collection": "score_elss_cap"
    },
    "Contra": {
        "score_collection": "score_contra_cap"
    },
    "Focused": {
        "score_collection": "score_focused_cap"
    }
}

MIN_DAILY_POINTS = 250

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

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "nav"])
    df = df.sort_values("date")
    df = df.set_index("date")

    return df


def get_cagr_fixed_year_daily(df, years):
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
# PHASE-3A RUNNER (FINAL)
# =========================
def run_phase_3a_for_category(category):
    if category not in CATEGORY_CONFIG:
        raise ValueError(f"Unsupported category: {category}")

    score_col = db[CATEGORY_CONFIG[category]["score_collection"]]

    # ✅ Growth is DEFAULT → exclude IDCW instead
    schemes = fund_col.find({
    "category": category,
    "$and": [
        {"scheme_name": {"$regex": "Direct", "$options": "i"}},
        {"scheme_name": {"$not": {"$regex": "IDCW|Dividend", "$options": "i"}}}
    ]
})



    eligible = 0
    excluded = 0

    for fund in schemes:
        scheme_code = fund["scheme_code"]
        scheme_name = fund["scheme_name"]

        df_daily = fetch_daily_nav(scheme_code)

        # -------------------------
        # ELIGIBILITY
        # -------------------------
        if df_daily is None or len(df_daily) < MIN_DAILY_POINTS:
            score_col.update_one(
                {"scheme_code": scheme_code},
                {
                    "$set": {
                        "scheme_name": scheme_name,
                        "category": category,
                        "phase3a_status": "excluded",
                        "exclusion_reason": "INSUFFICIENT_NAV_HISTORY",
                        "nav_stats": {
                            "points": 0 if df_daily is None else len(df_daily)
                        },
                        "meta": {
                            "last_updated": datetime.utcnow()
                        }
                    }
                },
                upsert=True
            )
            excluded += 1
            continue

        # -------------------------
        # PERFORMANCE
        # -------------------------
        perf = {}

        for y in [1, 3, 5]:
            val = get_cagr_fixed_year_daily(df_daily, y)
            if val is not None:
                perf[f"cagr_{y}y"] = val

        for m in [3, 6]:
            target_date = df_daily.index.max() - pd.DateOffset(months=m)
            df_start = df_daily[df_daily.index <= target_date]
            if not df_start.empty:
                start_nav = df_start.iloc[-1]["nav"]
                end_nav = df_daily.iloc[-1]["nav"]
                perf[f"return_{m}m"] = (end_nav / start_nav) - 1

        # -------------------------
        # RISK
        # -------------------------
        df_monthly = df_daily.resample("ME").last()
        log_returns = np.log(df_monthly["nav"] / df_monthly["nav"].shift(1)).dropna()

        risk = {
            "volatility": log_returns.std() * np.sqrt(12),
            "max_drawdown": max_drawdown(df_daily["nav"])
        }

        # -------------------------
        # WRITE
        # -------------------------
        score_col.update_one(
            {"scheme_code": scheme_code},
            {
                "$set": {
                    "scheme_name": scheme_name,
                    "category": category,
                    "metrics": {
                        "performance": perf,
                        "risk": risk
                    },
                    "nav_stats": {
                        "first_date": df_daily.index.min(),
                        "last_date": df_daily.index.max(),
                        "points": len(df_daily)
                    },
                    "phase3a_status": "eligible",
                    "exclusion_reason": None,
                    "meta": {
                        "cagr_method": "daily_fixed_calendar",
                        "risk_method": "monthly_log_from_daily",
                        "last_updated": datetime.utcnow()
                    }
                }
            },
            upsert=True
        )

        eligible += 1

    print(f"✅ Phase-3A complete for {category}")
    print("Eligible:", eligible)
    print("Excluded:", excluded)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run_phase_3a_for_category("Large Cap")
    run_phase_3a_for_category("Flexi Cap")
    run_phase_3a_for_category("Mid Cap")
    run_phase_3a_for_category("Small Cap")
    run_phase_3a_for_category("Multi Cap")
    run_phase_3a_for_category("Value")
    run_phase_3a_for_category("ELSS")
    run_phase_3a_for_category("Contra")
    run_phase_3a_for_category("Focused")