import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"

BLOCK_SECTIONS = (
    "debt",
    "derivative",
    "money market",
    "treps",
    "reverse repo",
)

def normalize(text):
    return (
        str(text)
        .lower()
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return val.startswith("INE") and len(val) == 12

def find_header_row(df):
    for i in range(min(30, len(df))):
        row = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "isin" in row and "% to net" in row:
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        col_norm = normalize(col)
        for kw in keywords:
            if kw in col_norm:
                return col
    return None

# -----------------------------
# MAIN PARSER
# -----------------------------

def parse_edelweiss_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found in {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of the instrument", "instrument"])
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(df.columns, ["rating", "industry"])
    col_weight = find_col(df.columns, ["% to net"])

    if not col_company or not col_isin or not col_weight:
        raise Exception(f"❌ Required columns missing in {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    current_blocked_section = False

    for _, row in df.iterrows():

        company = row[col_company]

        if pd.isna(company):
            continue

        company_norm = normalize(company)

        # 🔴 Detect section switches
        if any(s in company_norm for s in BLOCK_SECTIONS):
            current_blocked_section = True
            continue

        if "equity & equity" in company_norm:
            current_blocked_section = False
            continue

        # ❌ Skip non-equity sections
        if current_blocked_section:
            continue

        isin = row[col_isin]
        weight_raw = row[col_weight]

        if not is_valid_isin(isin):
            continue

        try:
            raw = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(raw) or raw <= 0:
            continue

        # ✅ FIXED: SCALE TO PERCENTAGE
        weight_pct = round(raw * 100, 4)

        holding = {
            "isin": str(isin).strip(),
            "company": str(company).strip(),
            "sector": (
                str(row[col_sector]).strip()
                if col_sector and pd.notna(row[col_sector])
                else ""
            ),
            "weight": weight_pct,
            "weight_num": weight_pct,
            "section": SECTION_EQUITY,
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    return holdings, dict(section_summary)
