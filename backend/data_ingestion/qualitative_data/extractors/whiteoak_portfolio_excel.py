import pandas as pd
import math
from collections import defaultdict

# =============================
# SECTIONS
# =============================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"
SECTION_REITS = "reits"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_header_row(df):
    for i in range(len(df)):
        row = df.iloc[i]
        text = " ".join(str(x).lower() for x in row.values if pd.notna(x))
        if "name of the instrument" in text and "% to" in text:
            return i
    return None

def find_col(header, keywords):
    for k in keywords:
        matches = header[header.str.contains(k, case=False, na=False)]
        if not matches.empty:
            return matches.index[0]
    raise Exception(f"❌ Column not found: {keywords}")

# -------------------------------------------------
# MAIN PARSER
# -------------------------------------------------

def parse_whiteoak_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = find_col(header, ["name"])
    COL_ISIN   = find_col(header, ["isin"])
    COL_SECTOR = find_col(header, ["industry"])
    COL_WEIGHT = find_col(header, ["% to net", "% to nav"])

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        # =================================================
        # SECTION SWITCHING (HEADERS)
        # =================================================

        # REITS / INVITS
        if (
            "(b) reits" in row_text
            or "(c) invits" in row_text
            or row_text.strip() == "reits"
            or row_text.strip() == "invits"
            or "real estate investment trust" in row_text
            or "infrastructure investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        # DERIVATIVES
        if (
            "details of commodity future" in row_text
            or "index future" in row_text
            or "futures" in row_text
            or "derivatives" in row_text
        ):
            current_section = SECTION_DERIVATIVES
            continue

        # EQUITY
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        # DEBT
        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        # CASH
        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        # OTHERS (generic headers)
        if (
            "exchange traded funds" in row_text
            or "mutual fund units" in row_text
            or "alternative investment fund units" in row_text
        ):
            current_section = SECTION_OTHERS
            continue

        # =================================================
        # ROW PARSING
        # =================================================

        raw_name = row[COL_NAME]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()

        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        # -----------------------------------------
        # ETF / FOF DETECTION AT NAME LEVEL
        # -----------------------------------------

        name_lower = raw_name.lower()

        if (
            "gold etf" in name_lower
            or "silver etf" in name_lower
            or "foreign etf" in name_lower
            or "overseas etf" in name_lower
            or "international etf" in name_lower
            or ("etf" in name_lower and "fund" in name_lower)
        ):
            current_section = SECTION_OTHERS

        # -----------------------------------------

        isin = row[COL_ISIN]
        isin = str(isin).strip() if is_valid_isin(isin) else None

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight):
            continue

        # WhiteOak gives fractions (0–1)
        if weight <= 1:
            weight *= 100

        weight = round(weight, 4)

        holding = {
            "isin": isin if current_section == SECTION_EQUITY else None,
            "company": raw_name,
            "sector": str(row[COL_SECTOR]).strip() if pd.notna(row[COL_SECTOR]) else "",
            "weight": weight,
            "weight_num": weight,
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)

    # -------------------------------------------------
    # ENSURE ALL SECTIONS EXIST
    # -------------------------------------------------

    for sec in [
        SECTION_EQUITY,
        SECTION_DEBT,
        SECTION_REITS,
        SECTION_DERIVATIVES,
        SECTION_CASH,
        SECTION_OTHERS,
    ]:
        section_summary.setdefault(sec, [])

    return holdings, dict(section_summary)
