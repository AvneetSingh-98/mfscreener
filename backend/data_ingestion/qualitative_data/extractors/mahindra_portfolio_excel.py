import pandas as pd
import math

# =========================
# HELPERS
# =========================

INVALID_PREFIXES = (
    "total",
    "sub total",
    "subtotal",
    "grand total",
    "equity & equity related",
    "listed",
    "awaiting",
    "unlisted",
    "money market",
    "treps",
    "repo",
    "net receivable",
    "payable",
    "derivatives",
)

def normalize(text):
    return str(text).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return val.startswith("INE") and len(val) == 12

def is_noise_row(company):
    txt = normalize(company)
    return txt.startswith(INVALID_PREFIXES)

# =========================
# CORE PARSER
# =========================

def parse_mahindra_fund(xls_path: str, sheet_name: str):
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    # 🔍 Find header row
    header_row = None
    for i in range(25):
        row = df.iloc[i].astype(str).str.lower()
        if "isin" in row.values and "% to net" in " ".join(row.values):
            header_row = i
            break

    if header_row is None:
        raise ValueError("❌ Header row not found")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # 🔎 Resolve columns
    def find_col(keywords):
        for c in df.columns:
            cl = str(c).lower()
            for k in keywords:
                if k in cl:
                    return c
        return None

    col_company = find_col(["name of the instrument", "instrument"])
    col_isin = find_col(["isin"])
    col_sector = find_col(["industry", "sector"])
    col_weight = find_col(["% to net"])

    if not col_company or not col_isin or not col_weight:
        raise ValueError("❌ Required columns missing")

    holdings = []

    for _, row in df.iterrows():
        isin = row.get(col_isin)
        if not is_valid_isin(isin):
            continue

        company = str(row.get(col_company, "")).strip()
        if not company or is_noise_row(company):
            continue

        raw_weight = row.get(col_weight)

        # 🚨 STRICT WEIGHT PARSING (THIS FIXES 947 BUG)
        try:
            weight = float(str(raw_weight).replace("%", "").strip())
        except:
            continue

        # 🔒 HARD GUARDRAILS
        if weight <= 0 or weight > 30:
            continue

        holdings.append({
            "isin": isin.strip(),
            "company": company,
            "sector": str(row.get(col_sector)).strip() if col_sector else None,
            "weight": round(weight, 2),
            "weight_num": round(weight, 2),
            "section": "equity",
        })

    return holdings
