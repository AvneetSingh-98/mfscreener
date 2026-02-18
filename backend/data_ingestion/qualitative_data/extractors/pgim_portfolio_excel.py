import pandas as pd
import math
from collections import defaultdict

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

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def normalize(text):
 
    return str(text).lower().strip()
def find_col(header, keywords):
    """
    Robust column finder for messy Excel headers
    """
    for idx, col in header.items():
        col_text = str(col).lower().strip()
        if all(k in col_text for k in keywords):
            return idx
    raise ValueError(f"❌ Column not found for keywords: {keywords}")

def find_header_row(df):
    REQUIRED_KEYS = [
        "name",
        "isin",
        "quantity",
        "%",
        "market"
    ]

    for i in range(len(df)):
        row = df.iloc[i].astype(str).str.lower()

        hits = 0
        for key in REQUIRED_KEYS:
            if any(key in cell for cell in row if cell != "nan"):
                hits += 1

        # PGIM header reliably matches ≥4 columns
        if hits >= 4:
            return i

    return None


def parse_pgim_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise ValueError(f"❌ Header not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME = find_col(header, ["name"])
    COL_ISIN = find_col(header, ["isin"])
    COL_SECTOR = find_col(header, ["industry"])
    COL_QTY = find_col(header, ["quantity"])
    COL_WEIGHT = find_col(header, ["%"])


    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    # 🚨 IMPORTANT: start AFTER header row, but skip junk rows dynamically
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
        # -------- DATA ROW --------
        name = row.iloc[COL_NAME]
        isin = row.iloc[COL_ISIN]
        sector = row.iloc[COL_SECTOR]
        weight_raw = row.iloc[COL_WEIGHT]

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

        if not math.isfinite(weight) :
            continue

        # PGIM gives direct %
        weight = round(weight, 4)

        holding = {
            "isin": str(isin).strip() if is_valid_isin(isin) else None,
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
