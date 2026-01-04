import pandas as pd
from collections import defaultdict

SECTION_EQUITY = "equity"

SKIP_KEYWORDS = [
    "total",
    "grand total",
    "sub total",
    "equity & equity related",
    "listed / awaiting",
    "listed/awaiting",
    "unlisted",
    "money market",
    "treps",
    "repo",
    "net receivable",
    "nav"
]

# ---------------------------
# Helpers
# ---------------------------

def find_header_row(df):
    for i in range(30):
        row = df.iloc[i].astype(str).str.lower()
        if "isin" in row.values and "% to net" in " ".join(row.values):
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        for kw in keywords:
            if kw in col.lower():
                return col
    return None

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return val.startswith("INE") and len(val) == 12

def is_noise_company(name):
    name = name.lower()
    return any(k in name for k in SKIP_KEYWORDS)

# ---------------------------
# MAIN PARSER
# ---------------------------

def parse_dsp_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of instrument", "instrument"])
    col_isin    = find_col(df.columns, ["isin"])
    col_sector  = find_col(df.columns, ["industry", "sector", "rating"])
    col_weight  = find_col(df.columns, ["% to net"])

    if not all([col_company, col_isin, col_weight]):
        raise Exception(f"❌ Required columns missing in {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    for _, row in df.iterrows():

        company = str(row[col_company]).strip()
        isin = str(row[col_isin]).strip()
        weight_raw = row[col_weight]

        if not company or is_noise_company(company):
            continue

        if not is_valid_isin(isin):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not (0 < weight <= 100):
            continue

        holding = {
            "isin": isin,
            "company": company,
            "sector": str(row[col_sector]).strip() if col_sector else "",
            "weight": weight,
            "weight_num": weight,
            "section": SECTION_EQUITY
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    return holdings, dict(section_summary)

