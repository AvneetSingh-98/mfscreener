import os
from dotenv import load_dotenv
import certifi
from pymongo import MongoClient
from collections import defaultdict, Counter

load_dotenv()

# =========================
# DB CONFIG
# =========================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"

HOLDINGS_COL = "portfolio_holdings_v2"
OUTPUT_COL = "qual_sector_concentration"

# =========================
# NORMALIZATION
# =========================
def normalize_sector(sector):
    if not sector:
        return None
    sector = sector.lower().strip()
    sector = sector.replace("&", "and")
    sector = " ".join(sector.split())
    return sector


# =========================
# ASSET TYPE DETECTION
# =========================
def get_asset_type(h):
    section = (h.get("section") or "").lower()
    isin = h.get("isin", "")

    if section.startswith("equity foreign"):
        return "foreign_equity"

    if isin and not isin.startswith("INE"):
        return "foreign_equity"

    if section.startswith("equity"):
        return "indian_equity"

    # fallback: treat missing section as indian equity
    if not section:
        return "indian_equity"

    return None


# =========================
# BUILD ISIN → SECTOR STATS
# =========================
def build_isin_sector_stats(holdings_col):
    """
    Builds:
    isin -> {sector: amc_count}
    (Indian equity only)
    """
    stats = defaultdict(lambda: Counter())

    for doc in holdings_col.find({}):
        amc = doc.get("amc")

        for h in doc.get("holdings", []):
            asset_type = get_asset_type(h)
            if asset_type != "indian_equity":
                continue

            isin = h.get("isin")
            sector = normalize_sector(h.get("sector"))

            if not isin or not sector:
                continue

            stats[isin][sector] += 1

    return stats


# =========================
# SECTOR RESOLUTION
# =========================
def resolve_sector(isin, asset_type, amc_sector, isin_sector_stats):
    amc_sector = normalize_sector(amc_sector)

    # foreign equity → trust AMC always
    if asset_type == "foreign_equity":
        return amc_sector

    # indian equity → majority logic
    sector_counts = isin_sector_stats.get(isin, {})
    total_amcs = sum(sector_counts.values())

    if total_amcs >= 3:
        return max(sector_counts, key=sector_counts.get)

    # fallback
    return amc_sector


# =========================
# SECTOR CONCENTRATION
# =========================
def compute_sector_concentration(fund_doc, isin_sector_stats):
    sector_weights = defaultdict(float)
    total_equity_weight = 0.0

    for h in fund_doc.get("holdings", []):
        asset_type = get_asset_type(h)
        if asset_type not in ("indian_equity", "foreign_equity"):
            continue

        raw_weight = h.get("weight") or h.get("weight_num")
        

        try:
          weight = float(raw_weight)
        except (TypeError, ValueError):
          continue


        isin = h.get("isin")
        amc_sector = h.get("sector") or h.get("industry")

        if not amc_sector:
            continue

        sector = resolve_sector(
            isin=isin,
            asset_type=asset_type,
            amc_sector=amc_sector,
            isin_sector_stats=isin_sector_stats
        )

        if not sector:
            continue

        sector_weights[sector] += weight
        total_equity_weight += weight

    # normalize to 100%
    if total_equity_weight > 0:
        for s in sector_weights:
            sector_weights[s] = round(
                (sector_weights[s] / total_equity_weight) * 100, 2
            )

    sorted_sectors = sorted(
        sector_weights.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_sector = sorted_sectors[0][1] if sorted_sectors else 0.0
    top_3_sector = round(sum(w for _, w in sorted_sectors[:3]), 2)

    return {
        "sector_weights": dict(sorted_sectors),
        "top_sector_pct": round(top_sector, 2),
        "top_3_sector_pct": top_3_sector,
        "sector_count": len(sector_weights),
        "high_sector_risk": top_sector > 35,
        "very_high_sector_risk": top_3_sector > 65
    }


# =========================
# MAIN PIPELINE
# =========================
def main():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]

    holdings_col = db[HOLDINGS_COL]
    out_col = db[OUTPUT_COL]

    print("🚀 Building ISIN sector statistics...")
    isin_sector_stats = build_isin_sector_stats(holdings_col)

    print("🚀 Computing sector concentration for funds...")

    count = 0
    for fund_doc in holdings_col.find({}):
        fund_key = fund_doc.get("fund_key")
        amc = fund_doc.get("amc")
        as_of = fund_doc.get("as_of")

        metrics = compute_sector_concentration(
            fund_doc,
            isin_sector_stats
        )

        out_col.update_one(
            {"fund_key": fund_key, "as_of": as_of},
            {"$set": {
                "fund_key": fund_key,
                "amc": amc,
                "as_of": as_of,
                "sector_concentration": metrics
            }},
            upsert=True
        )

        count += 1

    print(f"✅ Sector concentration completed for {count} funds")


if __name__ == "__main__":
    main()
