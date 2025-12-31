import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_MONEY_MARKET = "money_market"
SECTION_DERIVATIVES = "derivatives"

INVALID_PREFIXES = ("total", "sub total", "grand total")

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(str(x).lower() for x in df.iloc[i].values if pd.notna(x))
        if "isin" in text and "% to aum" in text:
            return i
    return None

def parse_sbi_portfolio_excel(xls_path, sheet_name):

    raw = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(raw)
    if header_row is None:
        raise Exception(f"❌ Header not found in SBI sheet: {sheet_name}")

    header = raw.iloc[header_row].astype(str).str.lower()

    COL_NAME   = header[header.str.contains("instrument")].index[0]
    COL_ISIN   = header[header.str.contains("isin")].index[0]
    COL_SECTOR = header[header.str.contains("industry")].index[0]
    COL_QTY    = header[header.str.contains("quantity")].index[0]
    COL_MV     = header[header.str.contains("market value")].index[0]
    COL_WT     = header[header.str.contains("% to aum")].index[0]

    holdings = []
    section_summary = defaultdict(list)
    current_section = None

    for i in range(header_row + 1, len(raw)):
        row = raw.iloc[i]
        text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        # ---- SECTION SWITCH ----
        if "equity & equity related" in text:
            current_section = SECTION_EQUITY
            continue
        if "debt instruments" in text:
            current_section = SECTION_DEBT
            continue
        if "money market instruments" in text:
            current_section = SECTION_MONEY_MARKET
            continue
        if "derivatives" in text:
            current_section = SECTION_DERIVATIVES
            continue

        # ---- DATA ----
        isin = row[COL_ISIN]
        if not is_valid_isin(isin):
            continue

        name = str(row[COL_NAME]).strip()
        if name.lower().startswith(INVALID_PREFIXES):
            continue

        try:
            weight = float(row[COL_WT])
        except:
            continue

        if not math.isfinite(weight):
            continue

        holding = {
            "isin": isin,
            "company": name,
            "sector": str(row[COL_SECTOR]).strip(),
            "quantity": float(row[COL_QTY]) if pd.notna(row[COL_QTY]) else None,
            "market_value": float(row[COL_MV]),
            "weight": round(weight, 4),
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)

    return holdings, dict(section_summary)
