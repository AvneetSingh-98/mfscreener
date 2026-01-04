import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"

INVALID_PREFIXES = (
    "equity",
    "listed",
    "awaiting",
    "subtotal",
    "total",
    "grand total",
    "money market",
    "treps",
    "repo",
    "reverse repo",
    "net receivable",
    "payable",
    "accrued",
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

def is_noise_row(company):
    txt = normalize(company)
    return txt.startswith(INVALID_PREFIXES)

def find_header_row(df):
    """
    Detect row containing ISIN + % To Net Assets
    """
    for i in range(min(30, len(df))):
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

def parse_groww_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(
        xls_path,
        sheet_name=sheet_name,
        header=None
    )

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found in Groww sheet {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of instrument"])
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(df.columns, ["rating", "industry"])
    col_weight = find_col(df.columns, ["% to net"])

    if not col_company or not col_isin or not col_weight:
        raise Exception(f"❌ Required columns missing in {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    for _, row in df.iterrows():

        company = row[col_company]
        isin = row[col_isin]
        weight_raw = row[col_weight]

        if pd.isna(company) or is_noise_row(company):
            continue

        if not is_valid_isin(isin):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())*100
        except:
            continue

        if not math.isfinite(weight):
            continue

        # IMPORTANT: Groww already gives % values
        if not (0 < weight <= 100):
            continue

        holding = {
            "isin": str(isin).strip(),
            "company": str(company).strip(),
            "sector": (
                str(row[col_sector]).strip()
                if col_sector and pd.notna(row[col_sector])
                else ""
            ),
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": SECTION_EQUITY,
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[SECTION_EQUITY].append(idx)

    return holdings, dict(section_summary)
