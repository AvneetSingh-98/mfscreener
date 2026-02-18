import pandas as pd
from collections import defaultdict
import math

# =====================
# SECTIONS
# =====================
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
    "net receivable",
    "net payable",
)

# =====================
# HELPERS
# =====================
def is_valid_isin(text):
    if not text:
        return False
    text = str(text).strip().upper()
    return len(text) == 12 and text.isalnum()

def find_header_row(df):
    """
    Shriram header looks like:
    Name of Instrument | ISIN | Industry/Rating | Quantity | Market Value | % to Net Assets
    """
    for i in range(len(df)):
        row = df.iloc[i]
        tokens = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )
        if (
            "name" in tokens
            and "instrument" in tokens
            and "isin" in tokens
            and "industry" in tokens
            and "%" in tokens
        ):
            return i
    return None

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

def find_weight_anywhere(row):
    """
    Fallback for MF / ETF rows where % column shifts
    """
    for val in row.values:
        try:
            w = float(str(val).replace("%", "").strip())
            if 0 < w <= 100:
                return w
        except:
            continue
    return None

# =====================
# MAIN PARSER
# =====================
def parse_shriram_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("instrument", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_WEIGHT = header[header.str.contains("%", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # =====================
        # SECTION SWITCHING
        # =====================
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        # 🔴 OVERRIDE: MF / ETF inside debt → OTHERS
        if "investment in mutual fund" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "exchange traded fund" in row_text or "etf" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "derivative" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if current_section is None:
            continue

        # =====================
        # DATA ROW
        # =====================
        raw_name = row[COL_NAME]
        raw_isin = row[COL_ISIN]
        raw_weight = row[COL_WEIGHT]
        sector = row[COL_SECTOR]

        if pd.isna(raw_name):
            continue

        name = str(raw_name).strip()
        if name.lower().startswith(INVALID_PREFIXES):
            continue

        isin = str(raw_isin).strip() if is_valid_isin(raw_isin) else None

        # ---- weight extraction ----
        weight = None

        if not pd.isna(raw_weight):
            try:
                weight = float(str(raw_weight).replace("%", "").strip())
            except:
                weight = None

        # 🔴 fallback for OTHERS (MF / ETF)
        if weight is None and current_section == SECTION_OTHERS:
            weight = find_weight_anywhere(row)

        if weight is None or not (0 < weight <= 100):
            continue

        sector = str(sector).strip() if pd.notna(sector) else ""

        # =====================
        # FINAL SECTION ASSIGN
        # =====================
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
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

