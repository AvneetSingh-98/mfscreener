import pandas as pd
import math
from collections import defaultdict

# =========================
# CONSTANTS
# =========================

SECTION_EQUITY = "equity"

INVALID_PREFIXES = (
    "total",
    "sub total",
    "grand total",
    "equity & equity related",
    "listed / awaiting",
    "listed/awaiting",
    "unlisted",
    "money market",
    "treasury",
    "treps",
    "repo",
    "reverse repo",
    "cash",
    "net receivable",
    "payable",
    "accrued",
    "call",
)

# =========================
# HELPERS
# =========================

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

def is_noise_row(company):
    txt = normalize(company)
    return txt.startswith(INVALID_PREFIXES)

def find_header_row(df):
    """
    Franklin headers always contain:
    - ISIN
    - % to Net Assets
    """
    for i in range(min(40, len(df))):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "isin" in row_text and "% to net" in row_text:
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        col_norm = normalize(col)
        for kw in keywords:
            if kw in col_norm:
                return col
    return None

# =========================
# MAIN PARSER
# =========================

def parse_franklin_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(
        xls_path,
        sheet_name=sheet_name,
        header=None
    )

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Franklin header row not found in sheet: {sheet_name}")

    # Set header
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Resolve columns
    col_company = find_col(
        df.columns,
        ["name of the instrument", "name of instrument", "instrument"]
    )
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(
        df.columns,
        ["industry classification", "industry"]
    )
    col_weight = find_col(
        df.columns,
        ["% to net assets", "% to net"]
    )

    if not col_company or not col_isin or not col_weight:
        raise Exception(
            f"❌ Required columns missing in Franklin sheet: {sheet_name}"
        )

    holdings = []
    section_summary = defaultdict(list)

    # =========================
    # ROW ITERATION
    # =========================

    for _, row in df.iterrows():

        company = row[col_company]
        isin = row[col_isin]
        weight_raw = row[col_weight]

        # Skip junk / section headers
        if pd.isna(company) or is_noise_row(company):
            continue

        # Only equity ISINs
        if not is_valid_isin(isin):
            continue

        # Parse weight (ALREADY percentage)
        try:
            wt = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(wt):
            continue

        # Franklin % must be between 0 and 100
        if wt <= 0 or wt > 100:
            continue

        # 🔒 FINAL FIX — NO MULTIPLICATION
        wt_pct = wt

        holding = {
            "isin": str(isin).strip(),
            "company": str(company).strip(),
            "sector": (
                str(row[col_sector]).strip()
                if col_sector and pd.notna(row[col_sector])
                else ""
            ),
            "weight": round(wt_pct, 4),              # e.g. 9.49
            "weight_num": round(wt_pct / 100, 6),    # e.g. 0.0949
            "section": SECTION_EQUITY,
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    if not holdings:
        raise Exception(
            f"❌ Franklin holdings empty after parsing ({sheet_name})"
        )

    return holdings, dict(section_summary)
