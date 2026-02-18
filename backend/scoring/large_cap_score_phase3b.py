import numpy as np
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi
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
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

nav_col = db["nav_history"]
benchmark_col = db["benchmark_nav"]

# =========================
# CATEGORY CONFIG
# =========================
CATEGORY_CONFIG = {
    "Large Cap": {"score_main": "score_large_cap", "score_consistency": "score_large_cap_consistency"},
    "Flexi Cap": {"score_main": "score_flexi_cap", "score_consistency": "score_flexi_cap_consistency"},
    "Mid Cap": {"score_main": "score_mid_cap", "score_consistency": "score_mid_cap_consistency"},
    "Small Cap": {"score_main": "score_small_cap", "score_consistency": "score_small_cap_consistency"},
    "Multi Cap": {"score_main": "score_multi_cap", "score_consistency": "score_multi_cap_consistency"},
    "Value": {"score_main": "score_value_cap", "score_consistency": "score_value_cap_consistency"},
    "ELSS": {"score_main": "score_elss_cap", "score_consistency": "score_elss_cap_consistency"},
    "Contra": {"score_main": "score_contra_cap", "score_consistency": "score_contra_cap_consistency"},
    "Focused": {"score_main": "score_focused_cap", "score_consistency": "score_focused_cap_consistency"},
    "Large & Mid Cap": {"score_main": "score_large_mid_cap", "score_consistency": "score_large_mid_cap_consistency"},
    # =========================
    # THEMATIC / SECTORAL
    # =========================

    "Banking & Financial Services": {
        "score_main": "score_banking_financial_services",
        "score_consistency": "score_banking_financial_services_consistency"
    },

    "Healthcare": {
        "score_main": "score_healthcare",
        "score_consistency": "score_healthcare_consistency"
    },

    "Infrastructure": {
        "score_main": "score_infrastructure",
        "score_consistency": "score_infrastructure_consistency"
    },

    "Consumption": {
        "score_main": "score_consumption",
        "score_consistency": "score_consumption_consistency"
    },

    "Business Cycle": {
        "score_main": "score_business_cycle",
        "score_consistency": "score_business_cycle_consistency"
    },

    "ESG": {
        "score_main": "score_esg",
        "score_consistency": "score_esg_consistency"
    },

    "Technology": {
        "score_main": "score_technology",
        "score_consistency": "score_technology_consistency"
    },

    # =========================
    # FACTOR / QUANT
    # =========================

    "Quant / Multi-Factor": {
        "score_main": "score_quant_multifactor",
        "score_consistency": "score_quant_multifactor_consistency"
    }
}

# =========================
# HELPERS
# =========================
def fetch_monthly_nav(collection, key, value):
    df = pd.DataFrame(
        list(collection.find({key: value}, {"date": 1, "nav": 1, "_id": 0}))
    )
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month").last().reset_index()


def rolling_cagr(series, window):
    values = []
    years = window / 12

    for i in range(window, len(series)):
        s = series.iloc[i - window]
        e = series.iloc[i]
        if s > 0 and e > 0:
            values.append((e / s) ** (1 / years) - 1)

    return values


def rolling_alpha(fund_nav, bench_nav, window):
    values = []
    years = window / 12

    merged = pd.DataFrame({"f": fund_nav, "b": bench_nav}).dropna()

    for i in range(window, len(merged)):
        fs, fe = merged["f"].iloc[i - window], merged["f"].iloc[i]
        bs, be = merged["b"].iloc[i - window], merged["b"].iloc[i]

        if fs > 0 and fe > 0 and bs > 0 and be > 0:
            fund_cagr = (fe / fs) ** (1 / years) - 1
            bench_cagr = (be / bs) ** (1 / years) - 1
            values.append(fund_cagr - bench_cagr)

    return values


# =========================
# PHASE-3B RUNNER
# =========================
def run_phase_3b_for_category(category):
    print(f"\n Phase-3B: {category}")

    cfg = CATEGORY_CONFIG[category]
    score_main_col = db[cfg["score_main"]]
    score_consistency_col = db[cfg["score_consistency"]]

    # 🔑 counters MUST be local
    updated = 0
    skipped = 0
    alpha_any = 0
    alpha_full = 0

    schemes = score_main_col.find(
        {"phase3a_status": "eligible"},
        {"scheme_code": 1, "benchmark.code": 1}
    )

    for s in schemes:
        scheme_code = s["scheme_code"]

        fund_df = fetch_monthly_nav(nav_col, "scheme_code", scheme_code)
        if fund_df is None:
            skipped += 1
            continue

        nav_series = fund_df["nav"]
        consistency = {}

        # ---------- ABSOLUTE ROLLING ----------
        for label, window in ROLLING_WINDOWS.items():
            vals = rolling_cagr(nav_series, window)
            if len(vals) >= MIN_POINTS[label]:
                consistency[f"rolling_{label}"] = {
                    "median": float(np.median(vals)) * 100,
                    "p25": float(np.percentile(vals, 25)) * 100,
                    "p75": float(np.percentile(vals, 75)) * 100,
                    "observations": len(vals)
                }

        # ---------- OPTIONAL ALPHA ----------
        benchmark_code = s.get("benchmark", {}).get("code")
        if benchmark_code:
            bench_df = fetch_monthly_nav(benchmark_col, "benchmark", benchmark_code)

            if bench_df is not None:
                merged = fund_df.merge(
                    bench_df,
                    on="month",
                    suffixes=("_fund", "_bench")
                ).dropna()

                for label, window in ROLLING_WINDOWS.items():
                    alpha_vals = rolling_alpha(
                        merged["nav_fund"],
                        merged["nav_bench"],
                        window
                    )

                    if len(alpha_vals) >= MIN_POINTS[label]:
                        consistency[f"rolling_alpha_{label}"] = {
                            "median": float(np.median(alpha_vals)) * 100,
                            "p25": float(np.percentile(alpha_vals, 25)) * 100,
                            "p75": float(np.percentile(alpha_vals, 75)) * 100,
                            "observations": len(alpha_vals)
                        }

        # ---------- ELIGIBILITY ----------
        has_absolute = any(
            k.startswith("rolling_") and not k.startswith("rolling_alpha")
            for k in consistency
        )

        if not has_absolute:
            skipped += 1
            continue

        # ---------- WRITE ----------
        score_consistency_col.update_one(
            {"scheme_code": scheme_code},
            {"$set": {
                "scheme_code": scheme_code,
                "category": category,
                "consistency": consistency,
                "meta": {
                    "frequency": "monthly",
                    "last_updated": datetime.utcnow()
                }
            }},
            upsert=True
        )

        # ---------- ALPHA STATS ----------
        has_alpha_3y = "rolling_alpha_3y" in consistency
        has_alpha_5y = "rolling_alpha_5y" in consistency

        if has_alpha_3y or has_alpha_5y:
            alpha_any += 1
        if has_alpha_3y and has_alpha_5y:
            alpha_full += 1

        updated += 1

    print(
        f"  Updated: {updated} | "
        f"  Skipped: {skipped} | "
        f"  Alpha(any): {alpha_any} | "
        f"  Alpha(3Y+5Y): {alpha_full}"
    )


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    for cat in CATEGORY_CONFIG:
        run_phase_3b_for_category(cat)
