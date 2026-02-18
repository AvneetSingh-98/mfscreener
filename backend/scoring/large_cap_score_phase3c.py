import numpy as np
import pandas as pd
import re
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
MANUAL_BENCHMARK_OVERRIDE = {# =========================
    # FLEXI CAP — MANUAL OVERRIDES (FIXED)
    # =========================

    "canararobecoflexicap": "NIFTY_500",
    "sbiflexicap": "NIFTY_500",
    "kotakflexicap": "NIFTY_500",
    "jmflexicap": "NIFTY_500",

        
    # Mid Cap (explicit overrides)
    "adityabirlasunlifemidcap": "NIFTY_MIDCAP_150",
    "hsbcmidcap": "NIFTY_MIDCAP_150",
    "invescoindiamidcap": "NIFTY_MIDCAP_150",
    "licmfmidcap": "NIFTY_MIDCAP_150",
    
    # Small Cap (explicit, verified)
    "bandhansmallcap": "NIFTY_SMALLCAP_250",
    "invescoindiasmallcap": "NIFTY_SMALLCAP_250",
    "licsmallcap": "NIFTY_SMALLCAP_250",
    
    # 🔥 Multi Cap (NEW)
    "nipponindiamulticap": "NIFTY_MULTICAP_500",
    "sundarammulticap": "NIFTY_MULTICAP_500",
    # VALUE FUNDS (CRISIL → CANONICAL)
    # =========================
    
    "aditya birla sun life value": "NIFTY_500",
    "axis value": "NIFTY_500",
    "bandhan value": "NIFTY_500",
    "baroda bnp paribas value": "NIFTY_500",
    "canara robeco value": "NIFTY_500",
    "hdfc value": "NIFTY_500",
    "iti value": "NIFTY_500",
    "jm value": "NIFTY_500",
    "mahindra manulife value": "NIFTY_500",
    "nippon india value": "NIFTY_500",
    "quant value": "NIFTY_500",
    "quantum value": "NIFTY_500",
    "sundaram value": "NIFTY_500",
    "tata value": "NIFTY_500",
    "templeton india value": "NIFTY_500",
    "uti value": "NIFTY_500",
    "union value": "NIFTY_500",
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

    "canararobecoelsstaxsaver": "NIFTY_500",
    "growwelsstaxsaverformerlyknownasindiabullstaxsavings": "NIFTY_500",

    # Nippon India ELSS (Tax Saver)
    "nipponindiataxsaver": "NIFTY_500",

    # HDFC ELSS (Long Term Advantage)
    "hdfclongtermadvantage": "NIFTY_500",
    # =========================
    # CONTRA — MANUAL OVERRIDES
    # =========================

    "sbicontra": "NIFTY_500",
    "invescoindia contra": "NIFTY_500",
    "kotak contra": "NIFTY_500",
         

    # =========================
    # FOCUSED — MANUAL OVERRIDES (CRISIL)
    # =========================

    "360onefocused": "NIFTY_500",

    "adityabirlasunlifefocused": "NIFTY_500",
    "axisfocused": "NIFTY_500",
    "bandhanfocused": "NIFTY_500",
    "barodabnpparibasfocused": "NIFTY_500",
    "canararobecofocused": "NIFTY_500",
    "dspfocused": "NIFTY_500",
    "edelweissfocused": "NIFTY_500",
    "franklinindiafocusedequity": "NIFTY_500",
    "hdfcfocused": "NIFTY_500",
    "hsbcfocused": "NIFTY_500",

    "iciciprudentialfocusedequity": "NIFTY_500",
    "itifocused": "NIFTY_500",
    "invescoindiafocused": "NIFTY_500",
    "jmfocused": "NIFTY_500",
    "kotakfocused": "NIFTY_500",
    "mahindramanulifefocused": "NIFTY_500",
    "miraeassetfocused": "NIFTY_500",
    "nipponindiafocused": "NIFTY_500",
    "oldbridgefocused": "NIFTY_500",
    "quantfocused": "NIFTY_500",
    "sbifocused": "NIFTY_500",
    "sundaramfocused": "NIFTY_500",
    "tatafocused": "NIFTY_500",
    "utifocused": "NIFTY_500",
    "unionfocused": "NIFTY_500",
    "licfocused": "NIFTY_500",
    "motilaloswalfocused25mof25": "NIFTY_500",
    # =========================
# LARGE & MID CAP — MANUAL OVERRIDES
# =========================

"edelweisslargemidcap": "NIFTY_LARGEMIDCAP_250",
"hsbclargemidcap": "NIFTY_LARGEMIDCAP_250",
"quantlargemidcap": "NIFTY_LARGEMIDCAP_250",
"sundaramlargeandmidcap": "NIFTY_LARGEMIDCAP_250",
"unionlargemidcap": "NIFTY_LARGEMIDCAP_250",
"barodabnpparibaslargeandmidcap": "NIFTY_LARGEMIDCAP_250",
# =========================
# LARGE CAP — MANUAL OVERRIDES (FIXED)
# =========================

"growwlargecapformerlyknownasindiabullsbluechip": "NIFTY_100",
"iciciprudentiallargecapbluechip": "NIFTY_100",
"sundaramlargecapformerlyknownassundarambluechip": "NIFTY_100",
# =========================
# BANKING & FINANCIAL SERVICES
# =========================
"adityabirlasunlifebankingandfinancialservices": "NIFTY_FINANCIAL_SERVICES",
"nipponindiabankingandfinancialservices": "NIFTY_FINANCIAL_SERVICES",
"hdfcbankingfinancialservices": "NIFTY_FINANCIAL_SERVICES",
"licbankingandfinancialservices": "NIFTY_FINANCIAL_SERVICES",
"taurusbankingfinancialservices": "NIFTY_FINANCIAL_SERVICES",
# =========================
# HEALTHCARE / PHARMA
# =========================
"adityabirlasunlifepharmaandhealthcare": "NIFTY_HEALTHCARE",
"itipharmaandhealthcare": "NIFTY_HEALTHCARE",
"nipponindiapharma": "NIFTY_HEALTHCARE",
"quanthealthcare": "NIFTY_HEALTHCARE",
"sbihealthcareopportunities": "NIFTY_HEALTHCARE",
"tataindiapharmahealthcare": "NIFTY_HEALTHCARE",
"utihealthcare": "NIFTY_HEALTHCARE",
"whiteoakcapitalpharmaandheathcare": "NIFTY_HEALTHCARE",
# =========================
# CONSUMPTION
# =========================
"nipponindiaconsumption": "NIFTY_INDIA_CONSUMPTION",
"sundaramconsumptionformerlyknownassundaramruralandconsumption": "NIFTY_INDIA_CONSUMPTION",
# =========================
# INFRASTRUCTURE
# =========================
"bandhaninfrastructure": "NIFTY_INFRASTRUCTURE",
"bankofindiamanufacturinginfrastructure": "NIFTY_INFRASTRUCTURE",
"canararobecoinfrastructure": "NIFTY_INFRASTRUCTURE",
"kotakinfrastructureeconomicreform": "NIFTY_INFRASTRUCTURE",
"nipponindiapowerinfra": "NIFTY_INFRASTRUCTURE",

# =========================
# QUANT / MULTI-FACTOR
# =========================
"nipponindiaquant": "NIFTY_200",
"tataquant": "NIFTY_200",
# =========================
# UNKNOWN FIX OVERRIDES
# =========================

"mahindramanulifebusinesscycle": "NIFTY_500",
"hsbcconsumption": "NIFTY_INDIA_CONSUMPTION",
"hdfctechnology": "NIFTY_IT",
"quantteck": "NIFTY_IT"

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
    "score_focused_cap",
    "score_large_mid_cap",
    # THEMATIC / SECTORAL
    # =========================
    "score_banking_financial_services",
    "score_healthcare",
    "score_infrastructure",
    "score_consumption",
    "score_business_cycle",
    "score_esg",
    "score_technology",

    # =========================
    # FACTOR
    # =========================
    "score_quant_multifactor"
]

# =========================
# DB CONNECTION
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
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
    """Switching to simple returns for industry standard alignment"""
    df["ret"] = df["nav"].pct_change()
    return df.dropna()

# =========================
# METRICS
# =========================
def sharpe(r):
    s = r.std()
    return None if s == 0 else ((r.mean() - RF_MONTHLY) / s) * np.sqrt(12)

def sortino(r):
    # 1. Calculate the 'Underperformance' for every month
    # If return > RF, underperformance is 0. If return < RF, it's the difference.
    diffs = r - RF_MONTHLY
    downside_sq = np.minimum(0, diffs)**2
    
    # 2. Average across ALL months (N=36), not just the bad ones
    ds = np.sqrt(downside_sq.mean())
    
    excess_return = r.mean() - RF_MONTHLY
    
    if ds == 0:
        return 99.0 if excess_return > 0 else 0.0
        
    # 3. Annualize the result
    return (excess_return / ds) * np.sqrt(12)

def beta(rs, rb):
    vb = np.var(rb)
    return None if vb == 0 else np.cov(rs, rb)[0][1] / vb
def upside_beta(rs, rb, min_points=6):
    """
    Sensitivity during positive benchmark months
    Higher is better
    """
    mask = rb > 0
    if mask.sum() < min_points:
        return None

    rs_up = rs[mask]
    rb_up = rb[mask]

    vb = np.var(rb_up)
    if vb == 0:
        return None

    return np.cov(rs_up, rb_up)[0][1] / vb


def downside_beta(rs, rb, min_points=6):
    """
    Sensitivity during negative benchmark months
    Lower is better
    """
    mask = rb < 0
    if mask.sum() < min_points:
        return None

    rs_down = rs[mask]
    rb_down = rb[mask]

    vb = np.var(rb_down)
    if vb == 0:
        return None

    return np.cov(rs_down, rb_down)[0][1] / vb


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
                    merged["ret_s"], merged["ret_b"]),
                "upside_beta_3y": upside_beta(
                    merged["ret_s"], merged["ret_b"] ),
                "downside_beta_3y": downside_beta(
                    merged["ret_s"], merged["ret_b"]),
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

        print(f"Phase-3C complete  - {col_name}")
        print("Updated:", updated, "Skipped:", skipped)

        total_updated += updated

    print("\n TOTAL UPDATED:", total_updated)

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    run_phase_3c()

