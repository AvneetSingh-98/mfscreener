import pandas as pd
import math
from collections import defaultdict

# =========================
# SECTIONS
# =========================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

# =========================
# CONSTANTS
# =========================

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
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
        "infrastructure investment trust"
    ])

# =========================
# HEADER FINDER
# =========================

def find_header_row(df):
    for i in range(min(50, len(df))):
        row_text = " ".join(
            str(x).lower() for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in row_text and "% to net" in row_text:
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

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name of the instrument", "instrument"])
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(df.columns, ["industry classification", "industry"])
    col_weight = find_col(df.columns, ["% to net"])

    if not col_company or not col_weight:
        raise Exception(f"❌ Required columns missing in sheet: {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # ROW LOOP
    # =========================

    for i in range(len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # -------------------------
        # SECTION SWITCHING
        # -------------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "future" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
        ):
            current_section = SECTION_REITS
            continue

        # -------------------------
        # DATA EXTRACTION
        # -------------------------

        raw_name = row[col_company]
        weight_raw = row[col_weight]
        sector = row[col_sector] if col_sector else ""

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()
        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = find_isin_anywhere(row)

        sector = str(sector).strip() if pd.notna(sector) else ""

        # Parse weight (Franklin gives % already)
        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight) or weight <= 0 or weight > 100:
            continue

        # -------------------------
        # 🔥 FINAL SECTION OVERRIDE
        # -------------------------

        text = f"{name} {sector}".lower()

        if "etf" in text or "exchange traded fund" in text:
            section = SECTION_OTHERS

        elif current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None

        elif is_reit(name, sector):
            section = SECTION_REITS

        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": round(weight, 4),
            "weight_num": round(weight / 100, 6),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    if not holdings:
        raise Exception(f"❌ Franklin holdings empty after parsing {sheet_name}")

    return holdings, dict(section_summary)


