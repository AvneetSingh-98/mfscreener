import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"

INVALID_PREFIXES = (
    "total",
    "sub total",
    "grand total",
)

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_scheme_bounds(df, scheme_code):
    start = None
    end = None

    for i in range(len(df)):
        cell = str(df.iloc[i, 0]).upper()
        if f"SCHEME CODE{scheme_code}STARTS" in cell:
            start = i
        if f"SCHEME CODE{scheme_code}ENDS" in cell:
            end = i
            break

    if start is None or end is None:
        raise Exception(f"❌ Scheme code {scheme_code} bounds not found")

    return start, end

def find_header_row(df, start, end):
    for i in range(start, end):
        row_text = " ".join(
            str(x).lower() for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in row_text and "% to nav" in row_text:
            return i
    return None

def parse_uti_portfolio_excel(xls_path, scheme_code):

    df = pd.read_excel(xls_path, header=None)

    start, end = find_scheme_bounds(df, scheme_code)

    header_row = find_header_row(df, start, end)
    if header_row is None:
        raise Exception(f"❌ Header not found for scheme {scheme_code}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_WEIGHT = header[header.str.contains("% to nav", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for i in range(header_row + 1, end):
        row = df.iloc[i]

        row_text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        if "debt" in row_text:
            current_section = SECTION_DEBT
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
        if current_section == SECTION_EQUITY and not isin:
            continue

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight):
            continue

        # 🔒 UTI % IS ALREADY PERCENTAGE — DO NOT SCALE
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
