import numpy as np
import pandas as pd
import re
from datetime import datetime
from pymongo import MongoClient
MANUAL_BENCHMARK_OVERRIDE = {
    "canara robeco flexicap": "BSE_500",
    "jm flexicap": "BSE_500",
    "sbi flexicap": "BSE_500",
    "kotak flexicap": "NIFTY_500",
    # Mid Cap (explicit overrides)
    "adityabirlasunlifemidcap": "NIFTY_MIDCAP_150",
    "hsbcmidcap": "NIFTY_MIDCAP_150",
    "invescoindiamidcap": "NIFTY_MIDCAP_150",
    "licmfmidcap": "NIFTY_MIDCAP_150",
    
    # Small Cap (explicit, verified)
    "bandhansmallcap": "BSE_SMALLCAP_250",
    "invescoindiasmallcap": "BSE_SMALLCAP_250",
    "licsmallcap": "NIFTY_SMALLCAP_250",
    
    # 🔥 Multi Cap (NEW)
    "nipponindiamulticap": "NIFTY_MULTICAP_500",
    "sundarammulticap": "NIFTY_MULTICAP_500",
    # VALUE FUNDS (CRISIL → CANONICAL)
    # =========================
    
    "aditya birla sun life value": "NIFTY_500",
    "axis value": "NIFTY_500",
    "bandhan value": "BSE_500",
    "baroda bnp paribas value": "NIFTY_500",
    "canara robeco value": "BSE_500",
    "hdfc value": "NIFTY_500",
    "iti value": "NIFTY_500",
    "jm value": "BSE_500",
    "mahindra manulife value": "NIFTY_500",
    "nippon india value": "NIFTY_500",
    "quant value": "NIFTY_500",
    "quantum value": "BSE_500",
    "sundaram value": "NIFTY_500",
    "tata value": "NIFTY_500",
    "templeton india value": "NIFTY_500",
    "uti value": "NIFTY_500",
    "union value": "BSE_500",
    # Groww (formerly Indiabulls)
    "growwvalueformerlyknownasindiabullsvalue": "NIFTY_500",

    # LIC
    "licvalue": "NIFTY_500",

    # ICICI Prudential (erstwhile Value Discovery)
    "iciciprudentialvaluevaluediscovery": "NIFTY_500",

    # HSBC
    "hsbcvalue": "NIFTY_500",
    # =========================
    # ELSS — MANUAL OVERRIDES
    # =========================

    "canararobecoelsstaxsaver": "BSE_500",
    "growwelsstaxsaverformerlyknownasindiabullstaxsavings": "BSE_500",

    # Nippon India ELSS (Tax Saver)
    "nipponindiataxsaver": "NIFTY_500",

    # HDFC ELSS (Long Term Advantage)
    "hdfclongtermadvantage": "NIFTY_500",
    # =========================
    # CONTRA — MANUAL OVERRIDES
    # =========================

    "sbicontra": "BSE_500",
    "invescoindia contra": "BSE_500",
    "kotak contra": "NIFTY_500",
         

    # =========================
    # FOCUSED — MANUAL OVERRIDES (CRISIL)
    # =========================

    "360onefocused": "BSE_500",

    "adityabirlasunlifefocused": "NIFTY_500",
    "axisfocused": "NIFTY_500",
    "bandhanfocused": "BSE_500",
    "barodabnpparibasfocused": "NIFTY_500",
    "canararobecofocused": "BSE_500",
    "dspfocused": "NIFTY_500",
    "edelweissfocused": "NIFTY_500",
    "franklinindiafocusedequity": "NIFTY_500",
    "hdfcfocused": "NIFTY_500",
    "hsbcfocused": "NIFTY_500",

    "iciciprudentialfocusedequity": "BSE_500",
    "itifocused": "NIFTY_500",
    "invescoindiafocused": "BSE_500",
    "jmfocused": "BSE_500",
    "kotakfocused": "NIFTY_500",
    "mahindramanulifefocused": "NIFTY_500",
    "miraeassetfocused": "NIFTY_500",
    "nipponindiafocused": "BSE_500",
    "oldbridgefocused": "BSE_500",
    "quantfocused": "NIFTY_500",
    "sbifocused": "BSE_500",
    "sundaramfocused": "NIFTY_500",
    "tatafocused": "NIFTY_500",
    "utifocused": "NIFTY_500",
    "unionfocused": "BSE_500",
    "licfocused": "NIFTY_500",
    "motilaloswalfocused25mof25": "NIFTY_500"
}

# =========================
# CONFIG
# =========================
LOOKBACK_MONTHS = 36
MIN_MONTHS = 30
# =========================
# CATEGORY DEFAULT BENCHMARKS (PHASE-3C ONLY)
# =========================


RISK_FREE_RATE = 0.06
RF_MONTHLY = RISK_FREE_RATE / 12

# All score collections to process
SCORE_COLLECTIONS = [
    "score_large_cap",
    "score_flexi_cap",
    "score_mid_cap",
    "score_small_cap",
    "score_multi_cap",
    "score_value_cap",
    "score_elss_cap",
    "score_contra_cap",
    "score_focused_cap"
]

# =========================
# DB CONNECTION
# =========================
client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]

nav_col       = db["nav_history"]
benchmark_col = db["benchmark_nav"]
fund_map_col  = db["fund_benchmark_map"]

# =========================
# CANONICAL NORMALIZATION
# (PHASE-3C ONLY – SAFE)
# =========================
def canon(name: str) -> str:
    """
    Canonicalize fund / scheme name defensively.
    This logic lives ONLY inside Phase-3C.
    """
    name = name.lower()

    for t in [
        "direct", "regular", "growth", "idcw", "dividend",
        "plan", "option", "fund","mf","erstwhile"
    ]:
        name = name.replace(t, "")

    # remove punctuation / hyphens / junk
    name = re.sub(r"[^a-z0-9 ]+", " ", name)

    # collapse spaces
    return " ".join(name.split())

# =========================
# NAV HELPERS
# =========================
def fetch_monthly_nav(collection, key, value):
    df = pd.DataFrame(
        list(collection.find({key: value}, {"date": 1, "nav": 1, "_id": 0}))
    )
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    df["month"] = df["date"].dt.to_period("M")
    return df.groupby("month").last().reset_index()

def log_returns(df):
    df["ret"] = np.log(df["nav"] / df["nav"].shift(1))
    return df.dropna()

# =========================
# METRICS
# =========================
def sharpe(r):
    s = r.std()
    return None if s == 0 else ((r.mean() - RF_MONTHLY) / s) * np.sqrt(12)

def sortino(r):
    d = r[r < RF_MONTHLY]
    if d.empty:
        return None
    ds = np.sqrt(((d - RF_MONTHLY) ** 2).mean())
    return None if ds == 0 else ((r.mean() - RF_MONTHLY) / ds) * np.sqrt(12)

def beta(rs, rb):
    vb = np.var(rb)
    return None if vb == 0 else np.cov(rs, rb)[0][1] / vb

def information_ratio(rs, rb):
    a = rs - rb
    s = a.std()
    return None if s == 0 else (a.mean() / s) * np.sqrt(12)

def clean(v):
    return None if v is None or np.isnan(v) else round(v, 4)

# =========================
# BUILD CANONICAL BENCHMARK MAP (IN-MEMORY)
# =========================
canonical_benchmark = {}

for row in fund_map_col.find({}):
    key = canon(row["fund_key"])
    # first one wins (CRISIL authoritative)
    if key not in canonical_benchmark:
        canonical_benchmark[key] = row["benchmark"]

# =========================
# MAIN RUNNER
# =========================
def run_phase_3c():
    total_updated = 0

    for col_name in SCORE_COLLECTIONS:
        if col_name not in db.list_collection_names():
            continue

        score_col = db[col_name]
        updated = skipped = 0

        cursor = score_col.find({
            "metrics.performance": {"$exists": True},
            "metrics.risk": {"$exists": True}
        })

        for fund in cursor:
            scheme_code = fund["scheme_code"]
            scheme_name = fund["scheme_name"]

            lookup_key = canon(scheme_name)
            benchmark = None
            benchmark_source = None
            

          # 1️⃣ Manual override FIRST (authoritative)
            for k, v in MANUAL_BENCHMARK_OVERRIDE.items():
                 if lookup_key.replace(" ", "") == k:

                   benchmark = v
                   benchmark_source = "manual_override"
                   break

         # 2️⃣ CRISIL / fund map next
            if not benchmark:
              bm = canonical_benchmark.get(lookup_key)
              if bm:
                 benchmark = bm
                 benchmark_source = "fund_map"

          

         # 4️⃣ Final skip
            if not benchmark:
              skipped += 1
              continue


            scheme_nav = fetch_monthly_nav(nav_col, "scheme_code", scheme_code)
            bench_nav  = fetch_monthly_nav(benchmark_col, "benchmark", benchmark)

            if scheme_nav is None or bench_nav is None:
                skipped += 1
                continue

            rs = log_returns(scheme_nav)
            rb = log_returns(bench_nav)

            merged = rs.merge(rb, on="month", suffixes=("_s", "_b")).dropna()
            merged = merged.tail(LOOKBACK_MONTHS)

            if len(merged) < MIN_MONTHS:
                skipped += 1
                continue

            metrics = {
                "sharpe_3y": sharpe(merged["ret_s"]),
                "sortino_3y": sortino(merged["ret_s"]),
                "information_ratio_3y": information_ratio(
                    merged["ret_s"], merged["ret_b"]),
                "beta_3y": beta(
                    merged["ret_s"], merged["ret_b"])
            }

            score_col.update_one(
                {"scheme_code": scheme_code},
                {"$set": {
                    "metrics.risk_adjusted": {
                        k: clean(v) for k, v in metrics.items()
                    },
                    "benchmark.code": benchmark,
                    "benchmark.source": benchmark_source,
                    "meta.phase_3c_updated": datetime.utcnow()
                }}
            )

            updated += 1

        print(f"✅ Phase-3C complete — {col_name}")
        print("Updated:", updated, "Skipped:", skipped)

        total_updated += updated

    print("\n📊 TOTAL UPDATED:", total_updated)

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_phase_3c()

