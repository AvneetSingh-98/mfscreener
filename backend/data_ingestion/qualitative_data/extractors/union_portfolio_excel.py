import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

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
    for val in row.values:
        if is_valid_isin(val):
            return str(val).strip()
    return None

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in ["reit", "invit"])

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(str(x).lower() for x in df.iloc[i].values if pd.notna(x))
        if "name of the instrument" in text and "% to nav" in text:
            return i
    return None

def detect_percent_column(df, qty_col_idx, start_row):
    best_col = None
    best_score = 0

    for col_idx in range(qty_col_idx + 1, min(qty_col_idx + 6, df.shape[1])):
        series = pd.to_numeric(
            df.iloc[start_row:, col_idx],
            errors="coerce"
        ).dropna()

        if len(series) < 10:
            continue

        score = ((series > 0) & (series <= 1)).mean()
        if score > best_score:
            best_score = score
            best_col = col_idx

    if best_col is None:
        raise Exception("❌ Could not detect % to NAV column")

    return best_col

def parse_union_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_QTY    = header[header.str.contains("quantity", case=False)].index[0]
    COL_WEIGHT = detect_percent_column(df, COL_QTY, header_row + 1)

    holdings = []
    section_summary = defaultdict(list)
    current_section = SECTION_EQUITY

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        row_text = " ".join(str(x).lower() for x in row.values if pd.notna(x))

        if any(x in row_text for x in [
            "debt instruments",
            "money market",
            "treasury bills",
            "reverse repo",
            "treps"
        ]):
            current_section = SECTION_DEBT
            continue

        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        raw_name = row[COL_NAME]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

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

        try:
            weight = float(weight_raw)
        except:
            continue

         # Union provides % directly
        if weight <= 0 or weight > 100:
          continue

        weight = round(weight, 4)


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
            "sector": str(sector).strip(),
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
