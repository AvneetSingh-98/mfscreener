import pandas as pd
import math
from collections import defaultdict

# =========================
# SECTIONS
# =========================

SECTION_EQUITY = "equity"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "portfolio",
)

# =========================
# HELPERS
# =========================

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def normalize(text):
    return str(text).lower().strip()

# =========================
# HEADER DETECTION (TAURUS)
# =========================

def find_header_row(df):
    for i in range(len(df)):
        row = df.iloc[i]
        text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        if (
            "name of the instrument" in text
            and "isin" in text
            and "quantity" in text
            and "% to aum" in text
        ):
            return i

    return None

# =========================
# MAIN PARSER
# =========================

def parse_taurus_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str).str.lower()

    COL_NAME   = header[header.str.contains("name of the instrument")].index[0]
    COL_ISIN   = header[header.str.contains("isin")].index[0]
    COL_SECTOR = header[header.str.contains("industry")].index[0]
    COL_QTY    = header[header.str.contains("quantity")].index[0]
    COL_WEIGHT = header[header.str.contains("% to aum")].index[0]

    current_section = None

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # -------------------------------
        # SECTION SWITCH
        # -------------------------------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if current_section != SECTION_EQUITY:
            continue

        # -------------------------------
        # DATA ROW
        # -------------------------------
        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if not is_valid_isin(isin):
            continue

        try:
            weight = float(weight_raw)
        except:
            continue

        # Taurus gives REAL %
        if not math.isfinite(weight) or weight <= 0 or weight > 100:
            continue

        weight = round(weight, 4)

        holding = {
            "isin": str(isin).strip(),
            "company": name,
            "sector": str(sector).strip() if pd.notna(sector) else "",
            "weight": weight,
            "weight_num": weight,
            "section": SECTION_EQUITY
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    return holdings, dict(section_summary)
