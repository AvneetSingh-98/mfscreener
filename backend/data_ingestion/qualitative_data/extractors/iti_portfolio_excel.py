# extractors/iti_portfolio_excel.py

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
    "net",
)

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
    return any(x in t for x in ["reit", "invit", "real estate investment trust"])

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(str(x).lower() for x in df.iloc[i].values if pd.notna(x))
        if "name of the instrument" in text and "%" in text and "net" in text:
            return i
    return None

# -------------------------------------------------
# MAIN PARSER
# -------------------------------------------------

def parse_iti_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME = header[header.str.contains("name of", case=False)].index[0]

    COL_ISIN = None
    if header.str.contains("isin", case=False).any():
        COL_ISIN = header[header.str.contains("isin", case=False)].index[0]

    COL_SECTOR = None
    if header.str.contains("industry", case=False).any():
        COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]

    COL_WEIGHT = header[header.str.contains("%", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # ---------------------------
    # LOOP ROWS
    # ---------------------------

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        # ===== SECTION SWITCH =====

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if row_text.strip() == "derivatives" or "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
        ):
            current_section = SECTION_REITS
            continue

        if current_section is None:
            current_section = SECTION_OTHERS

        # ===== DATA =====

        raw_name = row.iloc[COL_NAME]
        weight_raw = row.iloc[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()
        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = find_isin_anywhere(row)

        if current_section == SECTION_EQUITY and not isin:
            continue

        sector = ""
        if COL_SECTOR is not None:
            val = row.iloc[COL_SECTOR]
            if pd.notna(val):
                sector = str(val).strip()

        try:
           w = str(weight_raw).replace("%", "").strip()
           if w.startswith("(") and w.endswith(")"):
             w = "-" + w[1:-1]
           weight = float(w)
        except:
            continue

       

        weight = round(weight, 4)*100

        # ===== FINAL SECTION =====

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
