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
# FILTERS
# =========================

INVALID_PREFIXES = (
    "equity",
    "listed",
    "awaiting",
    "subtotal",
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

INVALID_CONTAINS = (
    "sub total",
    "subtotal",
    "grand total",
    "total",
)

# =========================
# HELPERS
# =========================

def normalize(text):
    return str(text).lower().replace("\n", " ").strip()

def find_header_row(df):
    for i in range(30):
        row = df.iloc[i].astype(str).str.lower()
        joined = " ".join(row.values)
        if "isin" in joined and "% to net" in joined:
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        name = normalize(col)
        for kw in keywords:
            if kw in name:
                return col
    return None

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def is_noise_company(name):
    name = normalize(name)

    if name.startswith(INVALID_PREFIXES):
        return True

    for k in INVALID_CONTAINS:
        if k in name:
            return True

    return False

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

# =========================
# MAIN PARSER
# =========================

def parse_mirae_portfolio(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise ValueError("❌ Could not detect header row")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name"])
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(df.columns, ["industry", "sector"])
    col_weight = find_col(df.columns, ["% to net"])

    if not col_company or not col_isin or not col_weight:
        raise ValueError("❌ Required columns missing")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # ROW LOOP
    # =========================

    for _, row in df.iterrows():

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # -------------------------
        # SECTION SWITCHING
        # -------------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "margin" in row_text or "derivatives" in row_text or "futures" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
            or "real estate investment trust" in row_text
            or "infrastructure investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        # -------------------------
        # DATA EXTRACTION
        # -------------------------

        company = str(row[col_company]).strip()
        isin_raw = row[col_isin]
        sector = str(row[col_sector]).strip() if col_sector else ""
        weight_raw = row[col_weight]

        if not company or is_noise_company(company):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if weight <= 0 or not math.isfinite(weight):
            continue

        # -------------------------
        # ISIN HANDLING (TWEAK)
        # -------------------------

        if is_valid_isin(isin_raw):
            isin = str(isin_raw).strip()
        else:
            isin = None

        # Equity must have ISIN
        if current_section == SECTION_EQUITY and not isin:
            continue

        # -------------------------
        # FINAL SECTION OVERRIDE
        # -------------------------

        if is_reit(company, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": company,
            "sector": sector,
            "weight": round(weight, 6),
            "weight_num": round(weight, 6),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

