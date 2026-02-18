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

INVALID_PREFIXES = (
    "total",
    "sub total",
    "subtotal",
    "grand total",
    "net current",
    "portfolio classification",
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
        "real estate investment trust"
    ])

# =========================
# SCHEME BOUNDS (UNCHANGED)
# =========================

def find_scheme_bounds(df, scheme_code):
    start = None
    end = None

    for i in range(len(df)):
        cell = str(df.iloc[i, 0]).upper()
        if f"SCHEME CODE{scheme_code}STARTS" in cell:
            start = i
        if f"SCHEME CODE{scheme_code}ENDS" in cell:
            end = i
            break

    if start is None or end is None:
        raise Exception(f"❌ Scheme code {scheme_code} bounds not found")

    return start, end

# =========================
# HEADER DETECTION (UNCHANGED)
# =========================

def find_header_row(df, start, end):
    for i in range(start, end):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in row_text and "% to nav" in row_text:
            return i
    return None

# =========================
# MAIN PARSER
# =========================

def parse_uti_portfolio_excel(xls_path, scheme_code):

    df = pd.read_excel(xls_path, header=None)

    start, end = find_scheme_bounds(df, scheme_code)

    header_row = find_header_row(df, start, end)
    if header_row is None:
        raise Exception(f"❌ Header not found for scheme {scheme_code}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_WEIGHT = header[header.str.contains("% to nav", case=False)].index[0]

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # ROW LOOP
    # =========================

    for i in range(header_row + 1, end):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )
        ##SECTION SWITCHING
        if "equity & equity related" in row_text:
         current_section = SECTION_EQUITY
         continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
           current_section = SECTION_DEBT
           continue
    
        
        if "treps" in row_text or "reverse repo" in row_text:
           current_section = SECTION_CASH
           continue

        if "FUTURES" in row_text or "derivatives" in row_text:
           current_section = SECTION_DERIVATIVES
           continue

        if (
            row_text.startswith("REIT")
            or row_text.startswith("reits")
            or row_text.startswith("INVIT")
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
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        lname = normalize(name)
        if any(x in lname for x in INVALID_PREFIXES):
            continue

        isin = str(isin).strip() if is_valid_isin(isin) else None

        if current_section == SECTION_EQUITY and not isin:
            continue

        sector = str(sector).strip() if pd.notna(sector) else ""

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # 🔒 UTI % ALREADY PERCENTAGE
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
