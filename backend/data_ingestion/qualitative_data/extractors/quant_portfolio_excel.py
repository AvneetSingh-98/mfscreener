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
SECTION_OTHERS = "others"
SECTION_CASH = "cash"

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


