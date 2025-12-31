import numpy as np
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# =========================
# CONFIG
# =========================
ROLLING_WINDOWS = {
    "3y": 36,
    "5y": 60
}

MIN_POINTS = {
    "3y": 20,
    "5y": 2
}

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

nav_col = db["nav_history"]

# =========================
# CATEGORY CONFIG
# =========================
CATEGORY_CONFIG = {
    "Large Cap": {
        "score_main": "score_large_cap",
        "score_consistency": "score_large_cap_consistency"
    },
    "Flexi Cap": {
        "score_main": "score_flexi_cap",
        "score_consistency": "score_flexi_cap_consistency"
    },
    "Mid Cap": {
        "score_main": "score_mid_cap",
        "score_consistency": "score_mid_cap_consistency"
    },
    "Small Cap": {
        "score_main": "score_small_cap",
        "score_consistency": "score_small_cap_consistency"
    },
    "Multi Cap": {
        "score_main": "score_multi_cap",
        "score_consistency": "score_multi_cap_consistency"
    },
    "Value": {
        "score_main": "score_value_cap",
        "score_consistency": "score_value_cap_consistency"
    },
    "ELSS": {
        "score_main": "score_elss_cap",
        "score_consistency": "score_elss_cap_consistency"
    },
    "Contra": {
        "score_main": "score_contra_cap",
        "score_consistency": "score_contra_cap_consistency"
    },
    "Focused": {
        "score_main": "score_focused_cap",
        "score_consistency": "score_focused_cap_consistency"
    }

}

# =========================
# HELPERS
# =========================
def fetch_monthly_nav(scheme_code):
    df = pd.DataFrame(
        list(nav_col.find(
            {"scheme_code": scheme_code},
            {"date": 1, "nav": 1, "_id": 0}
        ))
    )

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")

    # Month-end NAV (NO forward fill)
    df["month"] = df["date"].dt.to_period("M")
    df = df.groupby("month").last().reset_index()

    return df


def rolling_cagr(series, window):
    values = []
    years = window / 12

    for i in range(window, len(series)):
        start = series.iloc[i - window]
        end = series.iloc[i]

        if start > 0 and end > 0:
            values.append((end / start) ** (1 / years) - 1)

    return values


# =========================
# PHASE-3B RUNNER
# =========================
def run_phase_3b_for_category(category):
    if category not in CATEGORY_CONFIG:
        raise ValueError(f"Unsupported category: {category}")

    score_main_col = db[CATEGORY_CONFIG[category]["score_main"]]
    score_consistency_col = db[CATEGORY_CONFIG[category]["score_consistency"]]

    updated = 0
    skipped = 0

    schemes = score_main_col.find(
        {"phase3a_status": "eligible"},
        {"scheme_code": 1}
    )

    for s in schemes:
        scheme_code = s["scheme_code"]

        df = fetch_monthly_nav(scheme_code)
        if df is None:
            skipped += 1
            continue

        nav_series = df["nav"]
        consistency = {}

        for label, window in ROLLING_WINDOWS.items():
            values = rolling_cagr(nav_series, window)

            if len(values) < MIN_POINTS[label]:
                continue

            consistency[f"rolling_{label}"] = {
                "median": float(np.median(values)),
                "p25": float(np.percentile(values, 25)),
                "p75": float(np.percentile(values, 75)),
                "observations": len(values)
            }

        # No valid rolling window → skip (by policy)
        if not consistency:
            skipped += 1
            continue

        score_consistency_col.update_one(
            {"scheme_code": scheme_code},
            {
                "$set": {
                    "scheme_code": scheme_code,
                    "category": category,
                    "consistency": consistency,
                    "meta": {
                        "frequency": "monthly",
                        "last_updated": datetime.utcnow()
                    }
                }
            },
            upsert=True
        )

        updated += 1

    print(f"✅ Phase-3B complete for {category}")
    print("Updated:", updated)
    print("Skipped:", skipped)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    
    run_phase_3b_for_category("Focused")