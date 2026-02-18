import numpy as np
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient

# =========================
# DB CONNECTION
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

nav_col = db["nav_history"]
fund_col = db["fund_master"]

# =========================
# CATEGORY CONFIG
# =========================
CATEGORY_CONFIG = {
    "Large Cap": {"score_collection": "score_large_cap"},
    "Flexi Cap": {"score_collection": "score_flexi_cap"},
    "Mid Cap": {"score_collection": "score_mid_cap"},
    "Large & Mid Cap": {"score_collection": "score_large_mid_cap"},
    "Small Cap": {"score_collection": "score_small_cap"},
    "Multi Cap": {"score_collection": "score_multi_cap"},
    "Value": {"score_collection": "score_value_cap"},
    "ELSS": {"score_collection": "score_elss_cap"},
    "Contra": {"score_collection": "score_contra_cap"},
    "Focused": {"score_collection": "score_focused_cap"},
    "Banking & Financial Services": {
        "score_collection": "score_banking_financial_services"
    },

    "Healthcare": {
        "score_collection": "score_healthcare"
    },

    "Infrastructure": {
        "score_collection": "score_infrastructure"
    },

    "Consumption": {
        "score_collection": "score_consumption"
    },

    "Business Cycle": {
        "score_collection": "score_business_cycle"
    },

    "ESG": {
        "score_collection": "score_esg"
    },

    "Technology": {
        "score_collection": "score_technology"
    },

    "Quant / Multi-Factor": {
        "score_collection": "score_quant_multifactor"
    }
}
CATEGORY_KEYWORDS = {
    "Healthcare": {
        "include": [
            r"healthcare", r"pharma", r"health", r"diagnostics"
        ]
    },

    "Infrastructure": {
        "include": [
            r"infrastructure", r"infra", r"tiger"
        ]
    },

    "Consumption": {
        "include": [
            r"consumption", r"consumer", r"bharat consumption"
        ]
    },

    "Business Cycle": {
        "include": [
            r"business cycle"
        ]
    },

    "ESG": {
        "include": [
            r"esg"
        ]
    },

    "Technology": {
      "include": [
         r"technology fund",
         r"digital india",
         r"information technology",
         r"digital bharat",
         r"Teck",
         r"technology oppurtunities"
         r"\bit\b"
        ]
    },


    "Quant / Multi-Factor": {
       "include": [
          r"quant fund",
          r"quantamental",
          r"multi[- ]factor"
       ]
    }

}

GLOBAL_EXCLUDE_REGEX = (
    r"index fund|etf|fof|fund of fund|target maturity|gilt|bond|debt|"
    r"liquid|overnight|ultra short|short duration|medium duration|"
    r"money market|psu debt|credit risk|dynamic bond|banking & psu debt"
)

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
    df = df.sort_values("date").set_index("date")
    return df
def build_keyword_query(cfg):
    q = {"$and": []}

    # Direct + Growth
    q["$and"].append({
        "scheme_name": {"$regex": r"\bdirect\b", "$options": "i"}
    })
    q["$and"].append({
        "scheme_name": {"$regex": r"\bgrowth\b", "$options": "i"}
    })

    # Global block
    q["$and"].append({
        "scheme_name": {
            "$not": {"$regex": GLOBAL_EXCLUDE_REGEX, "$options": "i"}
        }
    })

    # Category include
    if "custom_include_regex" in cfg:
        q["$and"].append({
            "scheme_name": {
                "$regex": cfg["custom_include_regex"],
                "$options": "i"
            }
        })
    else:
        q["$and"].append({
            "scheme_name": {
                "$regex": r"\b(" + "|".join(cfg["include"]) + r")\b",
                "$options": "i"
            }
        })

    # Category exclude
    if "exclude" in cfg:
        q["$and"].append({
            "scheme_name": {
                "$not": {
                    "$regex": r"\b(" + "|".join(cfg["exclude"]) + r")\b",
                    "$options": "i"
                }
            }
        })

    return q



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

    return ((end_nav / start_nav) ** (1 / years) - 1)*100


def max_drawdown(series):
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return (drawdown.min())*100


# =========================
# PHASE-3A RUNNER (FINAL)
# =========================
def run_phase_3a_for_category(category):
    if category not in CATEGORY_CONFIG:
        raise ValueError(f"Unsupported category: {category}")

    score_col = db[CATEGORY_CONFIG[category]["score_collection"]]

    # -------------------------
    # BASE FILTER (COMMON)
    # -------------------------
    query = {
        "$and": [
            {"scheme_name": {"$regex": "Direct", "$options": "i"}},
            {"scheme_name": {"$not": {"$regex": "IDCW|Dividend", "$options": "i"}}}
        ]
    }

    # -------------------------
    # CATEGORY-SPECIFIC UNIVERSE
    # -------------------------
    if category == "Large & Mid Cap":
        query.update({
            "category": "Mid Cap",
            "sub_category": "Large & Mid Cap"
        })

    elif category == "Mid Cap":
        query.update({
            "category": "Mid Cap",
            "sub_category": {"$ne": "Large & Mid Cap"}
        })
    elif category == "Banking & Financial Services":
     query.update({
        "category": "Sectoral/ Thematic",

        "$and": [

            # -----------------------------
            # Must be Direct + Growth
            # -----------------------------
            {
                "scheme_name": {
                    "$regex": r"\bdirect\b",
                    "$options": "i"
                }
            },
            {
                "scheme_name": {
                    "$regex": r"\bgrowth\b",
                    "$options": "i"
                }
            },

            # -----------------------------
            # Must explicitly indicate BFSI
            # -----------------------------
            {
                "scheme_name": {
                    "$regex": r"(banking\s*&?\s*financial\s*services|financial\s*services|bfsi)",
                    "$options": "i"
                }
            },

            # -----------------------------
            # HARD EXCLUSIONS
            # -----------------------------
            {
                "scheme_name": {
                    "$not": {
                        "$regex": r"(index|etf|fof|fund\s*of\s*funds|arbitrage|hybrid|multi\s*asset|balanced|conservative|credit\s*risk|debt|bond|liquid|gilt|overnight|money\s*market|psu\s*debt|dynamic\s*bond)",
                        "$options": "i"
                    }
                }
            }
        ]
    })

    elif category in CATEGORY_KEYWORDS:
       cfg = CATEGORY_KEYWORDS[category]
       query = build_keyword_query(cfg)
    else:
        query.update({
            "category": category
        })

    schemes = fund_col.find(query)

    eligible = excluded = 0

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
                {"$set": {
                    "scheme_name": scheme_name,
                    "category": category,
                    "phase3a_status": "excluded",
                    "exclusion_reason": "INSUFFICIENT_NAV_HISTORY",
                    "nav_stats": {"points": 0 if df_daily is None else len(df_daily)},
                    "meta": {"last_updated": datetime.utcnow()}
                }},
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
                perf[f"return_{m}m"] = (
                    df_daily.iloc[-1]["nav"] / df_start.iloc[-1]["nav"] - 1
                )*100

        # -------------------------
        # RISK
        # -------------------------
        df_monthly = df_daily.resample("ME").last()
        log_returns = (np.log(df_monthly["nav"] / df_monthly["nav"].shift(1)).dropna())*100

        risk = {
            "volatility": (log_returns.std() * np.sqrt(12)),
            "max_drawdown": max_drawdown(df_daily["nav"])
        }

        # -------------------------
        # WRITE
        # -------------------------
        score_col.update_one(
            {"scheme_code": scheme_code},
            {"$set": {
                "scheme_name": scheme_name,
                "category": category,
                "metrics": {"performance": perf, "risk": risk},
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
            }},
            upsert=True
        )

        eligible += 1

    print(f"Phase-3A complete for {category}")
    print("Eligible:", eligible)
    print("Excluded:", excluded)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    for cat in CATEGORY_CONFIG:
        run_phase_3a_for_category(cat)
