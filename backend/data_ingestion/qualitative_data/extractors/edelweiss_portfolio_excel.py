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
    "net",
)

# -----------------------
# Helpers
# -----------------------

def normalize(x):
    return str(x).lower().replace("\n"," ").replace("\r"," ").strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def find_header_row(df):
    for i in range(min(40, len(df))):
        row = " ".join(normalize(x) for x in df.iloc[i].values if pd.notna(x))
        if "name of the instrument" in row and "% to net" in row:
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        c = normalize(col)
        for kw in keywords:
            if kw in c:
                return col
    return None

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

# -----------------------
# MAIN PARSER
# -----------------------

def parse_edelweiss_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found in {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of the instrument", "instrument"])
    col_isin    = find_col(df.columns, ["isin"])
    col_sector  = find_col(df.columns, ["rating", "industry"])
    col_weight  = find_col(df.columns, ["% to net"])

    if not col_company or not col_weight:
        raise Exception(f"❌ Required columns missing in {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for _, row in df.iterrows():

        company = row[col_company]

        if pd.isna(company):
            continue

        name = str(company).strip()
        name_norm = normalize(name)

        # -----------------------
        # SECTION SWITCHING
        # -----------------------

        if "equity & equity" in name_norm:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in name_norm or "money market" in name_norm:
            current_section = SECTION_DEBT
            continue

        if "derivatives" in name_norm or "index/stock future" in name_norm:
            current_section = SECTION_DERIVATIVES
            continue

        if "treps" in name_norm or "reverse repo" in name_norm:
            current_section = SECTION_CASH
            continue

        if "reit" in name_norm or "invit" in name_norm:
            current_section = SECTION_REITS
            continue

        if "others" in name_norm or "gold" in name_norm or "silver" in name_norm:
            current_section = SECTION_OTHERS
            continue

        if name_norm.startswith(INVALID_PREFIXES):
            continue

        # -----------------------
        # DATA
        # -----------------------

        isin = row[col_isin] if col_isin else None
        weight_raw = row[col_weight]

        try:
            weight = float(str(weight_raw).replace("%","").strip())
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # Edelweiss gives fractions (0.0107)
        if weight <= 1:
            weight = round(weight * 100, 4)
        else:
            weight = round(weight, 4)

        sector = ""
        if col_sector and pd.notna(row[col_sector]):
            sector = str(row[col_sector]).strip()

        if not is_valid_isin(isin):
            isin = None

        # REIT override
        if is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
