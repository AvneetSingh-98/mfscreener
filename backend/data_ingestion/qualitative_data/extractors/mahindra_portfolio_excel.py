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
# HELPERS
# =========================

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

def normalize(x):
    return str(x).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return val.startswith("INE") and len(val) == 12

def extract_name_isin(raw):
    raw = str(raw).strip()
    parts = raw.split()
    isin = next((p for p in parts if is_valid_isin(p)), None)
    name = raw.replace(isin, "").strip() if isin else raw
    return name, isin

def find_isin_anywhere(row):
    for v in row.values:
        if is_valid_isin(v):
            return str(v).strip()
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
# HEADER DETECTION
# =========================

def find_header_row(df):
    for i in range(len(df)):
        row = df.iloc[i]
        text = " ".join(normalize(x) for x in row.values if pd.notna(x))
        if "name of the instrument" in text and "% to net" in text:
            return i
    return None

# =========================
# MAIN PARSER
# =========================

def parse_mahindra_fund(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_COMPANY = header[header.str.contains("instrument", case=False)].index[0]
    COL_ISIN    = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR  = header[header.str.contains("industry|sector", case=False)].index[0]
    COL_WEIGHT  = header[header.str.contains("% to net", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # LOOP ROWS
    # =========================

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # ---------- SECTION SWITCHING ----------

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

        if "derivatives" in row_text or "future" in row_text:
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

        # ---------- DATA ROW ----------

        raw_name = row[COL_COMPANY]
        raw_isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()
        if raw_name.lower().startswith(INVALID_PREFIXES):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = raw_isin

        if not isin:
            isin = find_isin_anywhere(row)

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not (0 < weight <= 100):
            continue

        sector = str(sector).strip() if pd.notna(sector) else ""

        # ---------- FINAL SECTION ----------

        if current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None
        elif is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            
           "isin": str(isin).strip() if isin else None,
            "company": name,
            "sector": sector,
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

