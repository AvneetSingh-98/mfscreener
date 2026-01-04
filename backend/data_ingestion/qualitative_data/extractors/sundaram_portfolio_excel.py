import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net receivable",
    "net payable",
)

def normalize(text):
    return str(text).lower().strip()

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()

def parse_sundaram_portfolio_excel(xls_path, sheet_name):

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

        # ---------------- HEADER DETECTION ----------------
        if (
            "name of the instrument" in row_text
            and "isin" in row_text
            and "% of net" in row_text
        ):
            header_row = i
            for idx, val in enumerate(row.values):
                key = normalize(val)
                if "name of the instrument" in key:
                    col_map["name"] = idx
                elif key == "isin code" or key == "isin":
                    col_map["isin"] = idx
                elif "industry" in key:
                    col_map["sector"] = idx
                elif "% of net" in key:
                    col_map["weight"] = idx
            continue

        if header_row is None:
            continue

        # ---------------- SECTION SWITCH ----------------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "derivative" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

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
            weight = float(str(weight).replace("%", ""))
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # Sundaram already gives %
        weight = round(weight, 4)*100

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
