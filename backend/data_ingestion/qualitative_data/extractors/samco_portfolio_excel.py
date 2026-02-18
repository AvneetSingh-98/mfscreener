import pandas as pd
import math
from collections import defaultdict

# =============================
# SECTIONS
# =============================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_DERIVATIVES = "derivatives"
SECTION_REITS = "reits"
SECTION_OTHERS = "others"
SECTION_CASH = "cash"


INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
)

# =============================
# HELPERS
# =============================

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def normalize(x):
    return str(x).lower().strip()

def find_header_row(df):
    """
    SAMCO / PGIM style header:
    Name | ISIN | Industry | Quantity | Market | % to Net Assets
    """
    for i in range(len(df)):
        row = df.iloc[i]
        text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        if (
            "name" in text
            and "isin" in text
            and "quantity" in text
            and "%" in text
        ):
            return i
    return None

def find_col(header, keywords):
    for k in keywords:
        matches = header[header.str.contains(k, case=False)]
        if not matches.empty:
            return matches.index[0]
    raise ValueError(f"❌ Column not found for keywords: {keywords}")

# =============================
# MAIN PARSER
# =============================

def parse_samco_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise ValueError(f"❌ Header not found in SAMCO sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = find_col(header, ["name"])
    COL_ISIN   = find_col(header, ["isin"])
    COL_SECTOR = find_col(header, ["industry"])
    COL_QTY    = find_col(header, ["quantity"])
    COL_WEIGHT = find_col(header, ["%"])

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # SECTION SWITCHING
        # =================================================
        # =================================================

        if "equity & equity related" in row_text:
           current_section = SECTION_EQUITY
           continue
        # ETFs -> Others
        if "exchange traded funds" in row_text:
          current_section = SECTION_OTHERS
          continue

        if "etf" in row_text:
          current_section = SECTION_OTHERS


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
          
        # -------- DATA --------
        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(weight_raw)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # 🔑 SAMCO gives FRACTION
        if weight <= 1:
            weight *= 100

        weight = round(weight, 4)

        holding = {
            "isin": isin if current_section == SECTION_EQUITY else None,
            "company": name,
            "sector": str(sector).strip() if pd.notna(sector) else "",
            "weight": weight,
            "weight_num": weight,
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)

    return holdings, dict(section_summary)
