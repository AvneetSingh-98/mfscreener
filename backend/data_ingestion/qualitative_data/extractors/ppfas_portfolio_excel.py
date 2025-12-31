# backend/data_ingestion/qualitative_data/extractors/ppfas_portfolio_excel.py

import pandas as pd
import math
from collections import defaultdict

# -------------------------
# CONSTANTS
# -------------------------

EPSILON_WEIGHT = 0.005

SECTION_EQUITY = "equity"
SECTION_EQUITY_FOREIGN = "equity_foreign"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"

INVALID_NAME_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net receivable",
    "name of security",
    "plan / option",
    "options",
    "notes",
    "nil"
)

# -------------------------
# HELPERS
# -------------------------

def is_valid_isin(isin: str) -> bool:
    if not isin:
        return False
    isin = str(isin).strip().upper()
    if isin in ("NIL", "NA", "NONE"):
        return False
    return len(isin) == 12 and isin.isalnum()

def is_reit_holding(name: str, sector: str) -> bool:
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate trust",
        "business parks",
        "office parks"
    ])

# -------------------------
# MAIN PARSER
# -------------------------

def parse_ppfas_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    current_section = None

    for _, row in df.iterrows():

        # ---------- ROW TEXT ----------
        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # ---------- SECTION DETECTION ----------
        if "equity & equity related foreign" in row_text:
            current_section = SECTION_EQUITY_FOREIGN
            continue

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "reit" in row_text or "invit" in row_text:
            current_section = SECTION_REITS
            continue

        if any(x in row_text for x in [
            "money market",
            "certificate of deposit",
            "commercial paper",
            "treasury bill",
            "debt instruments"
        ]):
            current_section = SECTION_DEBT
            continue

        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        # ---------- DATA ROW EXTRACTION ----------
        try:
            name = row.iloc[1]
            isin = row.iloc[2] if current_section != SECTION_DERIVATIVES else None
            sector = row.iloc[3] if len(row) > 3 else ""
        except Exception:
            continue

        if pd.isna(name):
            continue

        name = str(name).strip()
        sector = str(sector).strip() if pd.notna(sector) else ""

        if name.lower().startswith(INVALID_NAME_PREFIXES):
            continue

        # ---------- ISIN VALIDATION ----------
        if current_section != SECTION_DERIVATIVES:
            if not is_valid_isin(isin):
                continue

        # ---------- WEIGHT PARSING ----------
        weight_cell = row.iloc[6] if len(row) > 6 else None
        weight_num = EPSILON_WEIGHT
        weight = "<0.01"

        if isinstance(weight_cell, (int, float)) and math.isfinite(weight_cell):
            raw = weight_cell * 100
            if raw >= 0.01:
                weight_num = raw
                weight = round(raw, 2)

        # ---------- FINAL SECTION ----------
        section = (
            SECTION_REITS
            if current_section != SECTION_DERIVATIVES
            and is_reit_holding(name, sector)
            else current_section
        )

        # ---------- FINAL HOLDING ----------
        holding = {
            "company": name,
            "isin": isin if current_section != SECTION_DERIVATIVES else None,
            "sector": sector,
            "weight": weight,
            "weight_num": weight_num,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)

        if section:
            section_summary[section].append(idx)

    return holdings, dict(section_summary)
