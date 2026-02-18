import pandas as pd
import math
from collections import defaultdict

# ==============================
# SECTIONS
# ==============================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "subtotal",
    "total",
    "grand total",
    "net receivable",
    "net payable",
    "net receivable/(payable)",
)


# ==============================
# HELPERS
# ==============================

def normalize(text):
    return str(text).lower().strip()

def is_valid_isin(isin):
    if not isin:
        return False
    isin = str(isin).strip().upper()
    return len(isin) == 12 and isin.isalnum()

# ==============================
# MAIN PARSER (ABSL-STYLE)
# ==============================

def parse_quantum_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    header_row = None
    col_map = {}
    current_section = None

    for i, row in df.iterrows():

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # ---------------- HEADER ----------------
        if (
            "name of instrument" in row_text
            and "isin" in row_text
            and "% to nav" in row_text
        ):
            header_row = i
            for idx, val in enumerate(row.values):
                key = normalize(val)
                if "name of instrument" in key:
                    col_map["name"] = idx
                elif key == "isin":
                    col_map["isin"] = idx
                elif "industry" in key:
                    col_map["sector"] = idx
                elif "% to nav" in key:
                    col_map["weight"] = idx
            continue

        if header_row is None:
            continue

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

        # ---------------- DATA ROW ----------------
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
        sector = str(sector).strip() if pd.notna(sector) else ""

        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(weight)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # Quantum gives FRACTION
        if weight <= 1:
            weight *= 100

        weight = round(weight, 4)

        holding = {
            "isin": isin if current_section == SECTION_EQUITY else None,
            "company": name,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[current_section].append(idx)

    return holdings, dict(section_summary)
