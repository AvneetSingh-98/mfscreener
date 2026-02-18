import pandas as pd
import math
from collections import defaultdict

# ==============================
# SECTIONS
# ==============================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_CASH = "cash"
SECTION_DERIVATIVES = "derivatives"
SECTION_REITS = "reits"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

# ==============================
# HELPERS
# ==============================

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
        text = " ".join(str(x).lower() for x in df.iloc[i].values if pd.notna(x))
        if "isin" in text and "% to aum" in text:
            return i
    return None

# ==============================
# MAIN PARSER
# ==============================

def parse_sbi_portfolio_excel(xls_path, sheet_name):

    raw = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(raw)
    if header_row is None:
        raise Exception(f"❌ Header not found in SBI sheet: {sheet_name}")

    header = raw.iloc[header_row].astype(str).str.lower()

    COL_NAME   = header[header.str.contains("instrument")].index[0]
    COL_ISIN   = header[header.str.contains("isin")].index[0]
    COL_SECTOR = header[header.str.contains("industry")].index[0]
    COL_QTY    = header[header.str.contains("quantity")].index[0]
    COL_MV     = header[header.str.contains("market value")].index[0]
    COL_WT     = header[header.str.contains("% to aum")].index[0]

    holdings = []
    section_summary = defaultdict(list)
    current_section = None

    # ==============================
    # ROW LOOP
    # ==============================

    for i in range(header_row + 1, len(raw)):

        row = raw.iloc[i]

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # ---------- SECTION SWITCH ----------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "alternative investment fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "margin (future" in row_text or "derivatives" in row_text:
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

        if current_section is None:
            current_section = SECTION_OTHERS

        # ---------- DATA ----------
        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        qty = row[COL_QTY]
        mv = row[COL_MV]
        wt = row[COL_WT]

        if pd.isna(name) or pd.isna(wt):
            continue

        name = str(name).strip()
        if name.lower().startswith(INVALID_PREFIXES):
            continue

        isin = str(isin).strip() if pd.notna(isin) else None
        sector = str(sector).strip() if pd.notna(sector) else ""

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(str(wt).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        # safety for fractional weights
        

        weight = round(weight, 4)

        # ---------- FINAL SECTION ----------
        if current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None
        elif is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin if section == SECTION_EQUITY else None,
            "company": name,
            "sector": sector,
            "quantity": float(qty) if pd.notna(qty) else None,
            "market_value": float(mv) if pd.notna(mv) else None,
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
