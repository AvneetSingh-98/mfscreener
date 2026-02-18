import pandas as pd
import math
from collections import defaultdict

# ============================
# SECTIONS
# ============================

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
)

# ============================
# HELPERS
# ============================

def normalize(x):
    return str(x).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    v = str(val).strip().upper()
    return len(v) == 12 and v.isalnum()

def find_header_row(df):
    for i in range(len(df)):
        row = " ".join(normalize(x) for x in df.iloc[i].tolist())
        if "name of the instrument" in row and "% to nav" in row:
            return i
    return None

# ============================
# MAIN PARSER
# ============================

def parse_bandhan_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_WEIGHT = header[header.str.contains("%", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    # ==========================================================
    # LOOP
    # ==========================================================

    for i in range(header_row + 1, len(df)):

        row = df.iloc[i]

        colA = normalize(row[0])
        colB = normalize(row[1]) if len(row) > 1 else ""

        row_text = f"{colA} {colB}"

        # ----------------------------
        # SECTION SWITCHING
        # ----------------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "debt instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "money market instruments" in row_text:
            current_section = SECTION_CASH
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "international exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "reit" in row_text or "invit" in row_text:
            current_section = SECTION_REITS
            continue

        if "others" == colA:
            current_section = SECTION_OTHERS
            continue

        # ----------------------------
        # DATA ROW
        # ----------------------------

        name = row[COL_NAME]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()

        if name.lower().startswith(INVALID_PREFIXES):
            continue

        isin = row[COL_ISIN]
        isin = str(isin).strip() if is_valid_isin(isin) else None

        try:
            weight = float(str(weight_raw).replace("%", ""))
        except:
            continue

        # Bandhan gives 0-1 numbers
        if weight <= 1:
            weight *= 100

        if not math.isfinite(weight):
            continue

        weight = round(weight, 4)

        # ----------------------------
        # SECTION FINALIZATION
        # ----------------------------

        if current_section is None:
            section = SECTION_EQUITY
        else:
            section = current_section

        # Equity requires ISIN
        if section == SECTION_EQUITY and not isin:
            continue

        # Non-equity must NOT carry ISIN
        if section != SECTION_EQUITY:
            isin = None

        holding = {
            "isin": isin,
            "company": name,
            "sector": "",
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)


