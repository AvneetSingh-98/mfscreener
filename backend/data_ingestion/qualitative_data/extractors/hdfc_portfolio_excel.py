import pandas as pd
import math
from collections import defaultdict

# =====================================================
# SECTION CONSTANTS
# =====================================================

SECTION_EQUITY = "equity"
SECTION_EQUITY_FOREIGN = "equity_foreign"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"

EPSILON_WEIGHT = 0.005

# IMPORTANT:
# ❌ "others" REMOVED — HDFC REITs live under OTHERS
INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net current",
    "portfolio classification",
)

# =====================================================
# HELPERS
# =====================================================

def is_valid_isin(isin: str) -> bool:
    if not isin:
        return False
    isin = str(isin).strip().upper()
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

# =====================================================
# MAIN PARSER
# =====================================================

def parse_hdfc_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)
    current_section = None

    for _, row in df.iterrows():

        # ---------- ROW TEXT ----------
        row_text = " ".join(
            str(x).lower() for x in row.values if pd.notna(x)
        )

        # =================================================
        # SECTION DETECTION (ORDER MATTERS)
        # =================================================

        # 1️⃣ HDFC REIT / INVIT BLOCK
        if any(x in row_text for x in [
            "units issued by reit",
            "units issued by invit"
        ]):
            current_section = SECTION_REITS
            continue

        # 2️⃣ Equity (foreign first)
        if "equity & equity related foreign" in row_text:
            current_section = SECTION_EQUITY_FOREIGN
            continue

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        # 3️⃣ Derivatives (future-safe)
        if "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        # 4️⃣ Debt / Money Market
        if any(x in row_text for x in [
            "money market instruments",
            "debt instruments",
            "treps",
            "repo"
        ]):
            current_section = SECTION_DEBT
            continue

        # =================================================
        # DATA ROW EXTRACTION
        # =================================================

        try:
            isin = row.iloc[1] if current_section != SECTION_DERIVATIVES else None
            name = row.iloc[3]
            sector = row.iloc[4]
            weight = row.iloc[7]
        except Exception:
            continue

        if pd.isna(name) or pd.isna(weight):
            continue

        name = str(name).strip()
        sector = str(sector).strip() if pd.notna(sector) else ""

        if name.lower().startswith(INVALID_PREFIXES):
            continue

        # ---------- ISIN VALIDATION ----------
        if current_section != SECTION_DERIVATIVES:
            if not is_valid_isin(isin):
                continue

        # ---------- WEIGHT ----------
        try:
            weight = float(weight)
        except:
            continue

        if not math.isfinite(weight):
            continue

        weight_num = round(weight, 4)

        # =================================================
        # FINAL SECTION RESOLUTION
        # =================================================

        if current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
        elif is_reit_holding(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        # =================================================
        # FINAL HOLDING
        # =================================================

        holding = {
            "isin": isin if current_section != SECTION_DERIVATIVES else None,
            "company": name,
            "sector": sector,
            "weight": weight_num,
            "weight_num": weight_num,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)

        if section:
            section_summary[section].append(idx)

    return holdings, dict(section_summary)
