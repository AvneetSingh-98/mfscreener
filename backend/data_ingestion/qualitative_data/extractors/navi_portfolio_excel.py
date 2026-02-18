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
    "sub total",
    "total",
    "grand total",
    "net current",
)

# =========================
# HELPERS
# =========================

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(
            str(x).lower() for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in text and "% to net" in text:
            return i
    return None

# =========================
# MAIN PARSER
# =========================

def parse_navi_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str).str.lower()

    COL_NAME   = header[header.str.contains("name")].index[0]
    COL_ISIN   = header[header.str.contains("isin")].index[0]
    COL_SECTOR = header[header.str.contains("industry")].index[0]
    COL_WEIGHT = header[header.str.contains("% to net")].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY   # Navi sheets start with equity

    # =========================
    # ROW LOOP
    # =========================

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # -----------------------
        # SECTION SWITCHING
        # -----------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "futures" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
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

        # -----------------------
        # DATA EXTRACTION
        # -----------------------

        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()

        if name.lower().startswith(INVALID_PREFIXES):
            continue

        # -----------------------
        # WEIGHT
        # -----------------------

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        weight = round(weight, 4)   # Navi already gives %

        # -----------------------
        # ISIN RULE
        # -----------------------

        if current_section == SECTION_EQUITY:
            if not is_valid_isin(isin):
                continue
            isin = str(isin).strip()
        else:
            isin = None

        sector = str(sector).strip() if pd.notna(sector) else ""

        # -----------------------
        # FINAL SECTION OVERRIDE
        # -----------------------

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
