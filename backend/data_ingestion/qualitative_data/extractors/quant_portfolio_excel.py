import pandas as pd
import math
from collections import defaultdict
# backend/data_ingestion/qualitative_data/extractors/quant_portfolio_excel.py

# -------------------------
# SECTION CONSTANTS (ADD THIS)
# -------------------------
SECTION_EQUITY = "equity"
SECTION_EQUITY_FOREIGN = "equity_foreign"
SECTION_DERIVATIVES = "derivatives"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"

INVALID_NAME_PREFIXES = (
    "equity & equity",
    "listed / awaiting",
    "total",
    "sub total",
    "grand total",
    "scheme risk",
)

def is_valid_isin(isin: str) -> bool:
    if not isin:
        return False
    isin = str(isin).strip().upper()
    return len(isin) == 12 and isin.isalnum()

def parse_quant_portfolio_excel(xls_path, sheet_name):

    raw = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    for _, row in raw.iterrows():

        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # ---------- SECTION DETECTION ----------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "debt instruments" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        # ---------- DATA ROW ----------
        try:
            isin = row.iloc[1]
            name = row.iloc[2]
            industry = row.iloc[4]
            weight_cell = row.iloc[7]
        except Exception:
            continue

        if pd.isna(isin) or pd.isna(name):
            continue

        isin = str(isin).strip()
        name = str(name).strip()
        industry = str(industry).strip() if pd.notna(industry) else ""

        try:
            weight = float(weight_cell)
        except:
            continue

        if not math.isfinite(weight):
            continue

        holding = {
            "isin": isin,
            "company": name,
            "sector": industry,
            "weight": round(weight, 4),
            "section": current_section
        }

        idx = len(holdings)
        holdings.append(holding)

        if current_section:
            section_summary[current_section].append(idx)

    return holdings, dict(section_summary)


