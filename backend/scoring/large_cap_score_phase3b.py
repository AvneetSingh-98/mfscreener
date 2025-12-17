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
    "3y": 30,
    "5y": 50
}

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

nav_col = db["nav_history"]
score_consistency_col = db["score_large_cap_consistency"]
score_main_col = db["score_large_cap"]

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

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["month"] = df["date"].dt.to_period("M")
    df = df.groupby("month").last().reset_index()

    return df


def rolling_cagr(series, window):
    values = []
    for i in range(window, len(series)):
        start = series.iloc[i - window]
        end = series.iloc[i]
        years = window / 12
        if start > 0:
            values.append((end / start) ** (1 / years) - 1)
    return values


# =========================
# MAIN RUNNER
# =========================
def run_phase_3b():
    updated = 0
    skipped = 0

    schemes = score_main_col.find({}, {"scheme_code": 1})

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

        if not consistency:
            skipped += 1
            continue

        score_consistency_col.update_one(
            {"scheme_code": scheme_code},
            {
                "$set": {
                    "scheme_code": scheme_code,
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

    print("✅ Phase 3B complete")
    print("Updated:", updated)
    print("Skipped:", skipped)


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_phase_3b()
