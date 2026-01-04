import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
)

def normalize(x):
    return str(x).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_header_row(df):
    """
    Detect row containing:
    Name of Instrument | ISIN | % To Net Assets
    """
    for i in range(len(df)):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if (
            "name of instrument" in row_text
            and "isin" in row_text
            and "% to net" in row_text
        ):
            return i
    return None

def parse_unifi_portfolio_excel(xls_path):

    # 🔹 Unifi has only ONE sheet
    sheet_name = pd.ExcelFile(xls_path).sheet_names[0]
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception("❌ Header row not found in UNIFI file")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_WEIGHT = header[header.str.contains("%", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # -------------------------------
        # SECTION DETECTION
        # -------------------------------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if current_section != SECTION_EQUITY:
            continue

        # -------------------------------
        # DATA EXTRACTION
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

        if not math.isfinite(weight) or weight <= 0:
            continue

        # 🔒 Already in %
        weight = round(weight, 4)*100

        holding = {
            "isin": isin,
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
