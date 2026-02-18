# extractors/invesco_portfolio_excel.py

import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
    "net recievables/payables"
)

SKIP_KEYWORDS = [
    "scheme",
    "nav",
]

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def is_valid_isin(text):
    if not text:
        return False
    text = str(text).strip().upper()
    return len(text) == 12 and text.isalnum()

def extract_name_isin(raw):
    raw = str(raw).strip()
    parts = raw.split()
    isin = next((p for p in parts if is_valid_isin(p)), None)
    name = raw.replace(isin, "").strip() if isin else raw
    return name, isin

def find_isin_anywhere(row):
    for v in row.values:
        if is_valid_isin(v):
            return str(v).strip()
    return None

def is_reit(name, sector):
    t = f"{name} {sector}".lower()
    return any(k in t for k in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

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

    COL_COMPANY = find_col(df.columns, ["name of", "instrument", "security"])
    COL_SECTOR  = find_col(df.columns, ["industry", "sector"])
    COL_QTY     = find_col(df.columns, ["quantity"])
    COL_WEIGHT  = find_col(df.columns, ["% to net"])

    if not all([COL_COMPANY, COL_WEIGHT]):
        raise Exception(f"❌ Required columns missing in sheet: {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =================================================

    for _, row in df.iterrows():

        row_text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        # ------------- SECTION SWITCH -------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "alternative investment fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "futures" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
            or "real estate investment trust" in row_text
            or "infrastructure investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        # ------------- DATA -------------

        raw_name = row[COL_COMPANY]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()

        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        if any(k in raw_name.lower() for k in SKIP_KEYWORDS):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = find_isin_anywhere(row)

        if current_section == SECTION_EQUITY and not isin:
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        weight = round(weight, 4)
        sector = str(row[COL_SECTOR]).strip() if COL_SECTOR else ""

        # -------- FINAL SECTION --------

        if current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None
        elif is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

