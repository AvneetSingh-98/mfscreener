import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_DERIVATIVES = "derivatives"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
)

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(
            str(x).lower() for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in text and "% to net" in text:
            return i
    return None

def parse_navi_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str).str.lower()

    COL_NAME   = header[header.str.contains("name")].index[0]
    COL_ISIN   = header[header.str.contains("isin")].index[0]
    COL_SECTOR = header[header.str.contains("industry")].index[0]
    COL_WEIGHT = header[header.str.contains("% to net")].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # ---- section switches ----
        if "debt" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        if name.lower().startswith(INVALID_PREFIXES):
            continue

        isin = str(isin).strip() if is_valid_isin(isin) else None

        # strict ISIN only for equity
        if current_section == SECTION_EQUITY and not isin:
            continue

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # 🔑 Navi already provides %
        weight = round(weight, 4)

        holding = {
            "isin": isin,
            "company": name,
            "sector": str(sector).strip() if pd.notna(sector) else "",
            "weight": weight,
            "weight_num": weight,
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)

    return holdings, dict(section_summary)
