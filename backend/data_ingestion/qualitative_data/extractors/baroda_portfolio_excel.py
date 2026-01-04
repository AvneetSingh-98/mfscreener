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
    "net receivables",
    "net payables",
)

def normalize(text):
    return str(text).lower().strip()

def is_valid_isin(isin: str) -> bool:
    if not isin:
        return False
    isin = str(isin).strip().upper()
    return len(isin) == 12 and isin.isalnum()

def parse_baroda_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    header_found = False
    col_map = {}
    current_section = None

    for _, row in df.iterrows():

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # ---------------- HEADER ----------------
        if (
            "name of the instrument" in row_text
            and "isin" in row_text
            and "% to net" in row_text
        ):
            header_found = True
            for idx, val in enumerate(row.values):
                key = normalize(val)
                if "name of the instrument" in key:
                    col_map["name"] = idx
                elif key == "isin":
                    col_map["isin"] = idx
                elif "industry" in key or "sector" in key:
                    col_map["sector"] = idx
                elif "% to net" in key:
                    col_map["weight"] = idx
            continue

        if not header_found:
            continue

        # ---------------- SECTION SWITCH ----------------
        if "equity" in row_text and "related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text:
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

        if current_section == SECTION_EQUITY:
            if not is_valid_isin(isin):
                continue
        else:
            isin = None

        try:
            weight = float(weight)
        except:
            continue

        if not math.isfinite(weight) or weight <= 0:
            continue

        # Baroda gives % directly (still keep safety)
        if weight <= 1:
            weight *= 100

        weight = round(weight, 4)

        holding = {
            "isin": isin,
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
