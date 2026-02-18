import pandas as pd
import math
from collections import defaultdict

# =========================
# SECTIONS
# =========================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "subtotal",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

# =========================
# HELPERS
# =========================

def normalize(text):
    return str(text).lower().replace("\n"," ").replace("\r"," ").strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return val.startswith("INE") and len(val) == 12

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
    txt = f"{name} {sector}".lower()
    return any(x in txt for x in ["reit","invit","real estate investment trust"])

# =========================

def find_header_row(df):
    for i in range(min(40, len(df))):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of" in row_text and "isin" in row_text and "% to net" in row_text:
            return i
    return None

def find_col(columns, keywords):
    for c in columns:
        cn = normalize(c)
        for kw in keywords:
            if kw in cn:
                return c
    return None

# =========================
# MAIN PARSER
# =========================

def parse_groww_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in Groww sheet: {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    COL_COMPANY = find_col(df.columns, ["name of instrument","instrument"])
    COL_ISIN    = find_col(df.columns, ["isin"])
    COL_SECTOR  = find_col(df.columns, ["industry","rating"])
    COL_WEIGHT  = find_col(df.columns, ["% to net"])

    if not COL_COMPANY or not COL_WEIGHT:
        raise Exception(f"❌ Required columns missing in Groww sheet: {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # ITERATION
    # =========================

    for _, row in df.iterrows():

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # -------- SECTION HEADERS ONLY --------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "mutual fund" in row_text and "unit" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "margin (future" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
            or "real estate investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        # ----------------------------------

        raw_name = row[COL_COMPANY]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()
        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = find_isin_anywhere(row)

        # Equity rows must have ISIN
        if current_section == SECTION_EQUITY and not isin:
            continue

        sector = (
            str(row[COL_SECTOR]).strip()
            if COL_SECTOR and pd.notna(row[COL_SECTOR])
            else ""
        )

        try:
            weight = float(str(weight_raw).replace("%","").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        if not (0 < weight <= 100):
            continue
        weight=weight*100
        # =========================
        # 🎯 INSTRUMENT LEVEL OVERRIDE
        # =========================

        lname = name.lower()

        if "etf" in lname:
            section = SECTION_OTHERS

        elif is_reit(name, sector):
            section = SECTION_REITS

        elif current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None

        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": round(weight,4),
            "weight_num": round(weight,4),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    if not holdings:
        raise Exception(f"❌ No holdings parsed for Groww sheet {sheet_name}")

    return holdings, dict(section_summary)

