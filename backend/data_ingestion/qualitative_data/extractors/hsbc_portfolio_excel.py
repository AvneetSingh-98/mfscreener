import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

# -------------------------------------------------
# ISIN helpers
# -------------------------------------------------

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
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust",
    ])

# -------------------------------------------------
# Header detection (HSBC specific)
# -------------------------------------------------

def find_header_row(df):
    for i in range(len(df)):
        row = df.iloc[i]
        text = " ".join(str(x).lower() for x in row.values if pd.notna(x))
        if (
            "name of" in text
            and "isin" in text
            and "percentage" in text
        ):
            return i
    return None

# -------------------------------------------------
# MAIN PARSER
# -------------------------------------------------

def parse_hsbc_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_COMPANY = header[header.str.contains("name", case=False)].index[0]
    COL_SECTOR  = header[header.str.contains("rating|industry", case=False)].index[0]
    COL_QTY     = header[header.str.contains("quantity", case=False)].index[0]
    COL_WEIGHT  = header[header.str.contains("percentage", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # -------------------------------------------------
        # SECTION SWITCHING (STRICT ORDER)
        # -------------------------------------------------

        # ----- ALWAYS OTHERS -----
        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "exchange traded fund" in row_text or "etf" in row_text:
            current_section = SECTION_OTHERS
            continue

        # ----- EQUITY -----
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        # ----- DEBT / MONEY MARKET -----
        if (
            "debt instruments" in row_text
            or "money market instruments" in row_text
            or "commercial papers" in row_text
            or "fixed rate bonds" in row_text
        ):
            current_section = SECTION_DEBT
            continue

        # ----- DERIVATIVES -----
        if "derivative" in row_text or "futures" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        # ----- CASH -----
        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if current_section is None:
            continue

        # -------------------------------------------------
        # DATA ROW
        # -------------------------------------------------

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

        sector = (
            str(row[COL_SECTOR]).strip()
            if pd.notna(row[COL_SECTOR])
            else ""
        )

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # HSBC already gives fraction (0–1)
        weight = round(weight * 100, 4) if weight <= 1 else round(weight, 4)

        # -------------------------------------------------
        # FINAL SECTION OVERRIDE (SAFETY NET)
        # -------------------------------------------------

        if current_section == SECTION_OTHERS:
            section = SECTION_OTHERS
        elif is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        # Equity must have ISIN
        if section == SECTION_EQUITY and not isin:
            continue

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": section,
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
