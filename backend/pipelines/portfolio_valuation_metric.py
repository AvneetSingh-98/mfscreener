import os
from dotenv import load_dotenv
import certifi
import pandas as pd
from pymongo import MongoClient

load_dotenv()

# ================= CONFIG =================
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "mfscreener"
PORTFOLIO_COL = "portfolio_holdings_v2"

NSE_MASTER_CSV = "EQUITY_NSE.csv"
BSE_MASTER_CSV = "Equity_BSE.csv"
SCREENER_CSV = "screener_pe_pb_daily.csv"
# =========================================



def to_float(x):
    try:
        return float(x)
    except Exception:
        return None


# ------------------------------
# 1. Load NSE master (ISIN → NSE SYMBOL)
# ------------------------------
nse_df = pd.read_csv(NSE_MASTER_CSV, dtype=str)
nse_df.columns = nse_df.columns.str.strip()

nse_df["ISIN NUMBER"] = nse_df["ISIN NUMBER"].str.strip()
nse_df["SYMBOL"] = nse_df["SYMBOL"].str.strip()

isin_to_nse = dict(zip(nse_df["ISIN NUMBER"], nse_df["SYMBOL"]))


# ------------------------------
# 2. Load BSE master (ISIN → BSE CODE)
# ------------------------------
bse_df = pd.read_csv(BSE_MASTER_CSV, dtype=str)
bse_df.columns = bse_df.columns.str.strip()

bse_df["ISIN No"] = bse_df["ISIN No"].str.strip()
bse_df["Security Code"] = bse_df["Security Code"].str.strip()

isin_to_bse = dict(zip(bse_df["ISIN No"], bse_df["Security Code"]))


# ------------------------------
# 3. Load Screener valuations (SLUG BASED)
# ------------------------------
scr = pd.read_csv(SCREENER_CSV, dtype=str)
scr.columns = scr.columns.str.strip()

scr["slug"] = scr["slug"].str.strip()
scr["pe"] = scr["pe"].apply(to_float)
scr["pb"] = scr["pb"].apply(to_float)
scr["roe"] = scr["roe"].apply(to_float)

slug_to_roe = dict(zip(scr["slug"], scr["roe"]))
slug_to_pe = dict(zip(scr["slug"], scr["pe"]))
slug_to_pb = dict(zip(scr["slug"], scr["pb"]))
def detect_bandhan_equity(section_summary):
    """
    Bandhan-style equity:
    section_summary.equity is a list of holding objects, not indexes
    """
    if not section_summary:
        return False

    equity = section_summary.get("equity")
    if not isinstance(equity, list):
        return False

    # If list items are dicts with ISIN → Bandhan pattern
    return len(equity) > 0 and isinstance(equity[0], dict) and "isin" in equity[0]

def extract_equity_indexes(equity_list):
    """
    Supports:
    - [0,1,2]
    - [{index:0}, {index:1}]
    """
    indexes = set()

    for x in equity_list:
        if isinstance(x, int):
            indexes.add(x)
        elif isinstance(x, dict):
            idx = x.get("index")
            if isinstance(idx, int):
                indexes.add(idx)

    return indexes

# ------------------------------
# 4. Resolve stock valuation (ISIN → slug → PE/PB)
# ------------------------------
def get_stock_valuation(isin):
    pe = pb = roe = None

    # Try NSE symbol slug
    nse = isin_to_nse.get(isin)
    if nse:
        pe = slug_to_pe.get(nse)
        pb = slug_to_pb.get(nse)
        roe = slug_to_roe.get(nse)

    # Fallback to BSE code slug
    if pe is None or pb is None or roe is None:
        bse = isin_to_bse.get(isin)
        if bse:
            pe = pe if pe is not None else slug_to_pe.get(bse)
            pb = pb if pb is not None else slug_to_pb.get(bse)
            roe = roe if roe is not None else slug_to_roe.get(bse)

    return pe, pb, roe



# ------------------------------
# 5. Compute portfolio valuation (EQUITY ONLY)
# ------------------------------
def compute_portfolio_valuation(holdings, equity_indexes=None):
    pe_num = pe_den = 0.0
    pb_num = pb_den = 0.0
    roe_num = 0.0
    roe_den = 0.0
    roe_weight = 0.0

    pe_weight = pb_weight = 0.0
    total_equity_weight = 0.0

    for idx, h in enumerate(holdings):

        # If equity index list exists, enforce it
        if equity_indexes is not None and idx not in equity_indexes:
            continue

        isin = h.get("isin")
        w = to_float(h.get("weight")) or to_float(h.get("weight_num"))


        if not isin or not w or w <= 0:
            continue

        total_equity_weight += w

        pe, pb, roe = get_stock_valuation(isin)

        # ---- PE ----
        if pe and pe > 0:
           pe_num += w
           pe_den += w / pe
           pe_weight += w

        # ---- PB ----
        if pb and pb > 0:
           pb_num += w
           pb_den += w / pb
           pb_weight += w

        # ---- ROE (profitability quality signal) ----
        if roe is not None and pd.notna(roe):
           roe_num += w * roe
           roe_den += w
           roe_weight += w



    return {
    "portfolio_pe": round(pe_num / pe_den, 2) if pe_den > 0 else None,
    "portfolio_pb": round(pb_num / pb_den, 2) if pb_den > 0 else None,

    "portfolio_roe": round(roe_num / roe_den, 2) if roe_den > 0 else None,

    "pe_coverage_pct": round((pe_weight / total_equity_weight) * 100, 2)
        if total_equity_weight > 0 else 0,

    "pb_coverage_pct": round((pb_weight / total_equity_weight) * 100, 2)
        if total_equity_weight > 0 else 0,

    "roe_coverage_pct": round((roe_weight / total_equity_weight) * 100, 2)
        if total_equity_weight > 0 else 0,

    "equity_weight_total": round(total_equity_weight, 2),
}



# ------------------------------
# 6. Run for all portfolios
# ------------------------------
def main():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    col = db[PORTFOLIO_COL]

    print("🚀 Computing portfolio P/E & P/B (EQUITY ONLY)")

    updated = 0

    for doc in col.find({"as_of": "2025-12-31"}):
        holdings = doc.get("holdings", [])
        if not holdings:
            continue

        # -------- Determine equity indexes --------
        equity_indexes = None
        bandhan_equity_mode=False
        # Preferred: segregation_summary
        seg = doc.get("segregation_summary")
        if seg and isinstance(seg.get("equity"), list):
          equity_indexes = extract_equity_indexes(seg["equity"])

        # Fallback: section_summary
        if not equity_indexes:
           sec = doc.get("section_summary")
        if sec and isinstance(sec.get("equity"), list):
           equity_indexes = extract_equity_indexes(sec["equity"])


        # Preferred: segregation_summary
        seg = doc.get("segregation_summary")
        if seg and isinstance(seg.get("equity"), list):
            equity_indexes = set(seg["equity"])

        # Fallback: section_summary
        sec = doc.get("section_summary")
        if equity_indexes is None and sec and isinstance(sec.get("equity"), list):
            equity_indexes = set(sec["equity"])
        # 3️⃣ FINAL FALLBACK: Bandhan-style object equity
        if not equity_indexes:
           sec = doc.get("section_summary")
           if detect_bandhan_equity(sec):
             bandhan_equity_mode = True
        valuation = compute_portfolio_valuation(
            holdings,
            equity_indexes=None if bandhan_equity_mode else equity_indexes
        )

        col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"portfolio_valuation": valuation}}
        )

        updated += 1

    print(f"✅ Updated {updated} portfolios")


if __name__ == "__main__":
    main()
