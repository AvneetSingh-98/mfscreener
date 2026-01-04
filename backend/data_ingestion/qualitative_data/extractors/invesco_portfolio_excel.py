# extractors/invesco_portfolio_excel.py

import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"

SKIP_KEYWORDS = [
    "total",
    "grand total",
    "equity & equity related",
    "listed / awaiting",
    "unlisted",
    "mutual fund units",
    "triparty repo",
    "net current assets",
    "derivatives",
    "futures",
    "nav",
    "scheme"
]

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def find_header_row(df):
    for i in range(min(25, len(df))):
        row = df.iloc[i].astype(str).str.lower()
        joined = " ".join(row.values)
        if "isin" in joined and "% to net" in joined:
            return i
    return None


def find_col(columns, keywords):
    for col in columns:
        for kw in keywords:
            if kw in col.lower():
                return col
    return None


def is_valid_equity_row(row, col_isin, col_weight):
    isin = str(row[col_isin]).strip().upper()
    if not isin.startswith("INE"):
        return False

    try:
        float(str(row[col_weight]).replace("%", "").strip())
    except:
        return False

    return True


def is_noise_company(name):
    name = str(name).lower()
    return any(k in name for k in SKIP_KEYWORDS)

# -------------------------------------------------
# MAIN PARSER
# -------------------------------------------------

def parse_invesco_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name)
    header_row = find_header_row(df)

    if header_row is None:
        raise Exception(f"❌ Header row not found in sheet: {sheet_name}")

    df.columns = df.iloc[header_row].astype(str)
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of", "instrument", "security"])
    col_isin    = find_col(df.columns, ["isin"])
    col_sector  = find_col(df.columns, ["industry", "sector"])
    col_weight  = find_col(df.columns, ["% to net"])

    if not all([col_company, col_isin, col_weight]):
        raise Exception(f"❌ Required columns missing in sheet: {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    for _, row in df.iterrows():

        if not is_valid_equity_row(row, col_isin, col_weight):
            continue

        company = str(row[col_company]).strip()
        if is_noise_company(company):
            continue

        weight = float(str(row[col_weight]).replace("%", "").strip())
        if not math.isfinite(weight):
            continue

        holding = {
            "isin": str(row[col_isin]).strip(),
            "company": company,
            "sector": str(row[col_sector]).strip() if col_sector else None,
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": SECTION_EQUITY
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    return holdings, dict(section_summary)
