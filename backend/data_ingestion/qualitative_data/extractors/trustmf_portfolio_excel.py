import pandas as pd
import math
from collections import defaultdict

# =========================
# SECTIONS
# =========================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"
SECTION_REITS = "reits"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "portfolio classification",
    "Subtotal"
)

# =========================
# HELPERS
# =========================

def normalize(x):
    return str(x).lower().strip()

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

# =========================
# HEADER FINDER
# =========================

def find_header_row(df):
    for i in range(len(df)):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if (
            "name of instrument" in row_text
            and "isin" in row_text
            and "% to net assets" in row_text
        ):
            return i
    return None

# =========================
# MAIN PARSER
# =========================

def parse_trustmf_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]

    # sector column OPTIONAL
    sector_candidates = header[
        header.str.contains("industry|sector|classification", case=False, regex=True)
    ]
    COL_SECTOR = sector_candidates.index[0] if len(sector_candidates) > 0 else None

    COL_WEIGHT = header[header.str.contains("%", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    # =========================
    # ROW LOOP
    # =========================

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # -----------------------
        # SECTION SWITCHING
        # -----------------------

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

        # -----------------------
        # DATA EXTRACTION
        # -----------------------

        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR] if COL_SECTOR is not None else ""
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        isin = str(isin).strip() if pd.notna(isin) else None
        sector = str(sector).strip() if pd.notna(sector) else ""

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        # TRUSTMF gives percentage already
        if 0 < weight <= 1:
            weight *= 100

        if not (0 < weight <= 100):
            continue

        weight = round(weight, 4)

        # -----------------------
        # FINAL SECTION
        # -----------------------

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
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
