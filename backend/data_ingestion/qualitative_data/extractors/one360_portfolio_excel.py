import pandas as pd
import math
from collections import defaultdict
SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "total",
    "sub total",
    "grand total",
    "net",
)

def normalize(x):
    return str(x).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def parse_one360_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = None
    col_map = {}

    # ---------------------------
    # HEADER DETECTION
    # ---------------------------
    for i, row in df.iterrows():
        text = " ".join(normalize(x) for x in row.values if pd.notna(x))
        if (
            "name of the instrument" in text
            and "isin" in text
            and "rounded % to net assets" in text
        ):
            header_row = i
            for idx, val in enumerate(row.values):
                key = normalize(val)
                if "name of the instrument" in key:
                    col_map["name"] = idx
                elif key == "isin":
                    col_map["isin"] = idx
                elif "industry" in key:
                    col_map["sector"] = idx
                elif "rounded % to net assets" in key:
                    col_map["weight"] = idx
            break

    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    holdings = []
    section_summary = defaultdict(list)

        # ---------------------------
    # DATA ROWS
    # ---------------------------
    current_section = None

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
        if "etf" in row_text:
           current_section = SECTION_OTHERS
           continue

        if "mutual fund units" in row_text:
          current_section = SECTION_OTHERS
          continue

        if "alternative investment fund units" in row_text:
          current_section = SECTION_OTHERS
          continue

        if "treps" in row_text or "reverse repo" in row_text:
           current_section = SECTION_CASH
           continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
           current_section = SECTION_DEBT
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

        try:
            name = row.iloc[col_map["name"]]
            isin = row.iloc[col_map["isin"]]
            sector = row.iloc[col_map.get("sector", -1)]
            weight = row.iloc[col_map["weight"]]
        except Exception:
            continue

        if pd.isna(name) or pd.isna(weight):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if not is_valid_isin(isin):
            continue

        try:
            weight = float(weight) * 100
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        holding = {
            "isin": isin,
            "company": name,
            "sector": str(sector).strip() if pd.notna(sector) else "",
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)


    return holdings, dict(section_summary)
