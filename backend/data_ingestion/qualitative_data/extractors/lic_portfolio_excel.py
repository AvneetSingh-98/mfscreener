import pandas as pd
import math
from collections import defaultdict

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_CASH = "cash"
SECTION_REITS = "reits"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net",
)

def normalize(text):
    return str(text).lower().strip()

def is_valid_isin(isin):
    if not isin:
        return False
    isin = str(isin).strip().upper()
    return isin.startswith("INE") and len(isin) == 12

def parse_lic_portfolio_excel(xls_path, sheet_name):
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

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
            for idx, val in enumerate(row.values):
                key = normalize(val)
                if "name of the instrument" in key:
                    col_map["name"] = idx
                elif key == "isin":
                    col_map["isin"] = idx
                elif "industry" in key or "rating" in key:
                    col_map["sector"] = idx
                elif "% to net" in key:
                    col_map["weight"] = idx
            continue

        if not col_map:
            continue

        # ---------------- SECTION SWITCH ----------------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue
        if "debt instruments" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue
        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue
        if "reit" in row_text or "invit" in row_text:
            current_section = SECTION_REITS
            continue

        # 🔥 DEFAULT TO EQUITY (ICICI RULE)
        if current_section is None:
            current_section = SECTION_EQUITY

        # ---------------- DATA ROW ----------------
        try:
            name = row.iloc[col_map["name"]]
            isin = row.iloc[col_map["isin"]]
            sector = row.iloc[col_map.get("sector")]
            weight = row.iloc[col_map["weight"]]
        except:
            continue

        if pd.isna(name) or pd.isna(weight):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if current_section == SECTION_EQUITY:
            if not is_valid_isin(isin):
                continue

        try:
            weight = float(weight)*100
        except:
            continue

        if weight <= 0 or not math.isfinite(weight):
            continue

        holding = {
            "isin": str(isin).strip() if current_section == SECTION_EQUITY else None,
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
