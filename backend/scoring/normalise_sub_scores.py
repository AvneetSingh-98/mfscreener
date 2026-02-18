import numpy as np
from scipy.stats import rankdata
import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from datetime import datetime
import math

# =========================
# Mongo Config
# =========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["mfscreener"]

CATEGORY_MAP = {
    "Large Cap": "score_large_cap",
    "Mid Cap": "score_mid_cap",
    "Small Cap": "score_small_cap",
    "Large & Mid Cap": "score_large_mid_cap",
    "Flexi Cap": "score_flexi_cap",
    "Multi Cap": "score_multi_cap",
    "Value": "score_value_cap",
    "ELSS": "score_elss_cap",
    "Contra": "score_contra_cap",
    "Focused": "score_focused_cap",
    # NEW THEMATIC
    "Banking & Financial Services": "score_banking_financial_services",
    "Healthcare": "score_healthcare",
    "Infrastructure": "score_infrastructure",
    "Consumption": "score_consumption",
    "Business Cycle": "score_business_cycle",
    "ESG": "score_esg",
    "Technology": "score_technology",
    "Quant": "score_quant_multifactor"
}

MIN_FUNDS = 3

# =========================
# Helpers
# =========================
def clean_number(x):
    if x is None:
        return None
    try:
        return None if math.isnan(x) else x
    except TypeError:
        return x

def percentile_map(values, reverse=False):
    clean = [v for v in values if v is not None]
    if len(clean) < MIN_FUNDS:
        return {}

    arr = np.array(clean, dtype=float)
    if reverse:
        arr = -arr

    ranks = rankdata(arr, method="average") / len(arr) * 100
    return dict(zip(clean, ranks))

def extract_top10(ph):
    # 1️⃣ Preferred: standard field
    if ph.get("top_10_weight") is not None:
        return ph.get("top_10_weight")

    # 2️⃣ Kotak: metrics
    if ph.get("metrics", {}).get("top_10_equity") is not None:
        return ph["metrics"]["top_10_equity"]

    # 3️⃣ Kotak fallback: section_summary
    if ph.get("section_summary", {}).get("top_10_equity") is not None:
        return ph["section_summary"]["top_10_equity"]

    # 4️⃣ Absolute fallback
    return None

def symmetric_band(value, p10, p25, p75, p90):
    if value is None:
        return None

    # Core band
    if p25 <= value <= p75:
        return 75

    # Lower tail
    if value < p25:
        if p25 == p10:
            return 25
        score = 75 - (p25 - value) / (p25 - p10) * 50
        return max(25, round(score, 2))

    # Upper tail
    if value > p75:
        if p90 == p75:
            return 25
        score = 75 - (value - p75) / (p90 - p75) * 50
        return max(25, round(score, 2))

    return 25


def one_sided_penalty(value, p75, p90):
    if value is None:
        return None
    if value <= p75:
        return 75
    if value <= p90:
        return 75 - (value - p75) / (p90 - p75) * 25
    return 30

def consistency_confidence(obs_3y, obs_5y, max_3y=120, max_5y=96):
    """
    Returns confidence score in 0–100 range based on available rolling windows.
    """
    if obs_3y is None and obs_5y is None:
        return None

    c3 = obs_3y / max_3y if obs_3y else 0.0
    c5 = obs_5y / max_5y if obs_5y else 0.0

    confidence = 0.6 * c3 + 0.4 * c5
    return round(min(1.0, confidence) * 100, 2)

def calculate_hhi(sector_weights):
    if not sector_weights:
        return None
    return sum((w / 100) ** 2 for w in sector_weights.values())

def percentile_map_by_scheme(merged, field, reverse=False):
    data = [(m["scheme_code"], m[field]) for m in merged if m[field] is not None]
    if len(data) < MIN_FUNDS:
        return {}

    values = np.array([v for _, v in data], dtype=float)
    if reverse:
        values = -values

    pct = rankdata(values, method="average") / len(values) * 100
    return {code: float(pct[i]) for i, (code, _) in enumerate(data)}


# =========================
# Normalization Logic
# =========================
def normalize_category(category, score_coll):

    print(f"\n🔄 Normalizing {category}")
    score_docs = list(db[score_coll].find({}))
    if not score_docs:
        return

    merged = []

    for s in score_docs:
        scheme = s.get("scheme_code")
        fm = db.fund_master_v2.find_one({"scheme_code": scheme})
        if not fm:
            continue

        fund_key = fm["fund_key"]
        ph = db.portfolio_holdings_v2.find_one({"fund_key": fund_key})
        qs = db.qual_sector_concentration.find_one({"fund_key": fund_key})
        qa = db.qualitative_fund_attributes.find_one({"fund_key": fund_key})
        sc = db[f"{score_coll}_consistency"].find_one({"scheme_code": scheme})

        if not (ph and qs and qa):
            continue

        perf = s.get("metrics", {}).get("performance", {})
        risk = s.get("metrics", {}).get("risk", {})
        ra = s.get("metrics", {}).get("risk_adjusted", {})

        # ---- Consistency safe extraction ----
        # ---- Consistency (ALPHA-based) extraction ----
        alpha_3y = alpha_5y = alpha_iqr_3y = alpha_iqr_5y = None

        if sc and "consistency" in sc:
           a3 = sc["consistency"].get("rolling_alpha_3y")
           a5 = sc["consistency"].get("rolling_alpha_5y")

           if a3:
              alpha_3y = a3.get("median")
              if a3.get("p25") is not None and a3.get("p75") is not None:
                 alpha_iqr_3y = a3["p75"] - a3["p25"]

           if a5:
              alpha_5y = a5.get("median")
              if a5.get("p25") is not None and a5.get("p75") is not None:
                 alpha_iqr_5y = a5["p75"] - a5["p25"]

        pv = ph.get("portfolio_valuation", {})
        obs_3y = None
        obs_5y = None

        r3 = None
        r5 = None
        
        if sc and isinstance(sc.get("consistency"), dict):
          r3 = sc["consistency"].get("rolling_alpha_3y")
          r5 = sc["consistency"].get("rolling_alpha_5y")

        if isinstance(r3, dict):
          obs_3y = r3.get("observations")

        if isinstance(r5, dict):
           obs_5y = r5.get("observations")


        merged.append({
            "scheme_code": scheme,
            "fund_key": fund_key,

            # Returns
            "cagr_1y": perf.get("cagr_1y"),
            "cagr_3y": perf.get("cagr_3y"),
            "cagr_5y": perf.get("cagr_5y"),
            "return_3m": perf.get("return_3m"),
            "return_6m": perf.get("return_6m"),

            # Consistency
            "alpha_3y": alpha_3y,
            "alpha_5y": alpha_5y,
            "alpha_iqr_3y": alpha_iqr_3y,
            "alpha_iqr_5y": alpha_iqr_5y,

            "rolling_3y_obs": obs_3y,   # ⭐ ADD
            "rolling_5y_obs": obs_5y,

            # Risk
            "volatility": risk.get("volatility"),
            "max_dd": abs(risk.get("max_drawdown")) if risk.get("max_drawdown") is not None else None,

            # Risk adjusted
            "sharpe": ra.get("sharpe_3y"),
            "sortino": ra.get("sortino_3y"),
            "ir": ra.get("information_ratio_3y"),
            "up_beta": ra.get("upside_beta_3y"),
            "down_beta": ra.get("downside_beta_3y"),

            # Portfolio quality
            "stock_count": (
               ph.get("metrics", {}).get("equity_stock_count")
               if ph.get("metrics", {}).get("equity_stock_count") is not None
               else ph.get("equity_stock_count")
            ),
            "top10":  extract_top10(ph),
            "sector_hhi": calculate_hhi(qs["sector_concentration"]["sector_weights"]),
            "top3_sector": qs["sector_concentration"]["top_3_sector_pct"],
            "turnover": clean_number(qa.get("portfolio_turnover")),
            "ter": clean_number(qa.get("ter_direct_pct")),
            "aum": math.log(qa["monthly_avg_aum_cr"]) if qa.get("monthly_avg_aum_cr") else None,
            "manager_exp": max(
                [m.get("experience_years") for m in qa.get("fund_manager", []) if m.get("experience_years") is not None],
                default=None
            ),

            # Valuation
            "pe": pv.get("portfolio_pe"),
            "pb": pv.get("portfolio_pb"),
            "roe": pv.get("portfolio_roe"),
        })

    if len(merged) < MIN_FUNDS:
        return

    # -------- Percentile maps --------
    pm = {
        k: percentile_map([m[k] for m in merged], reverse=k in {
            "volatility","max_dd","iqr_3y","iqr_5y","ter","turnover","sector_hhi","down_beta","pe","pb"
        })
        for k in [
            "cagr_1y","cagr_3y","cagr_5y","return_3m","return_6m",
            "alpha_3y","alpha_5y","alpha_iqr_3y","alpha_iqr_5y",
            "volatility","max_dd",
            "sharpe","sortino","ir","up_beta","down_beta",
            "pe","pb","roe","sector_hhi","turnover","ter","manager_exp"
        ]
    }
    pm_turnover = percentile_map_by_scheme(merged, "turnover", reverse=True)

    # -------- Thresholds --------
    def pct_vals(k): return [m[k] for m in merged if m[k] is not None]

    p_stock = np.percentile(pct_vals("stock_count"), [10,25,75,90])
    p_aum   = np.percentile(pct_vals("aum"), [10,25,75,90])
    p_top10 = np.percentile(pct_vals("top10"), [75,90])
    p_top3  = np.percentile(pct_vals("top3_sector"), [75,90])

    out = []
    for m in merged:
        consistency_conf = consistency_confidence(
        m.get("rolling_3y_obs"),
        m.get("rolling_5y_obs")
        )   

        out.append({
            "scheme_code": m["scheme_code"],
            "fund_key": m["fund_key"],
            "category": category,

            "normalized_sub_scores": {
                "returns": {k: pm[k].get(m[k]) for k in ["cagr_1y","cagr_3y","cagr_5y","return_3m","return_6m"]},
                "consistency": {
                    **{k: pm[k].get(m[k]) for k in ["alpha_3y","alpha_5y","alpha_iqr_3y","alpha_iqr_5y",]},
                    "confidence": consistency_conf
                },
                "risk": {
                    "volatility": pm["volatility"].get(m["volatility"]),
                    "max_dd": pm["max_dd"].get(m["max_dd"]),
                    "up_beta": pm["up_beta"].get(m["up_beta"]),
                    "down_beta": pm["down_beta"].get(m["down_beta"]),
                },
                "risk_adjusted": {k: pm[k].get(m[k]) for k in ["sharpe","sortino","ir"]},
                "portfolio_quality": {
                    "stock_count": symmetric_band(m["stock_count"], *p_stock),
                    "aum": symmetric_band(m["aum"], *p_aum),
                    "top10": one_sided_penalty(m["top10"], *p_top10),
                    "sector_hhi": pm["sector_hhi"].get(m["sector_hhi"]),
                    "top3_sector": one_sided_penalty(m["top3_sector"], *p_top3),
                    "turnover": pm_turnover.get(m["scheme_code"]),
                    "ter": pm["ter"].get(m["ter"]),
                    "manager_experience": pm["manager_exp"].get(m["manager_exp"]),
                },
                "valuation": {k: pm[k].get(m[k]) for k in ["pe","pb","roe"]},
            },
            "meta": {
                "universe_size": len(merged),
                "normalized_at": datetime.utcnow()
            }
        })

    coll = f"normalized_{category.lower().replace(' ', '_')}_scores"
    db[coll].delete_many({})
    db[coll].insert_many(out)

    print(f"✅ Normalized {len(out)} funds")


if __name__ == "__main__":
    for cat, coll in CATEGORY_MAP.items():
        normalize_category(cat, coll)
