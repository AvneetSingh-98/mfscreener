import pandas as pd
import math
from collections import defaultdict

# ----------------------------
# Sections
# ----------------------------
SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

# ----------------------------
# Config (Kotak fixed layout)
# ----------------------------
COL_COMPANY = 2
COL_ISIN = 3
COL_SECTOR = 4
COL_WEIGHT = 8

# ----------------------------
# Helpers
# ----------------------------

def is_valid_isin(x):
    if not x:
        return False
    x = str(x).strip().upper()
    return len(x) == 12 and x.isalnum()

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(k in text for k in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

# ----------------------------
# MAIN PARSER
# ----------------------------

def parse_kotak_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    for _, row in df.iterrows():

        company = str(row[COL_COMPANY]).strip()
        isin = str(row[COL_ISIN]).strip()
        sector = str(row[COL_SECTOR]).strip()
        weight_raw = row[COL_WEIGHT]

        row_text = " ".join(
            str(x).lower()
            for x in row.values
            if pd.notna(x)
        )

        # ----------------------------
        # SECTION SWITCHING
        # ----------------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "futures" in row_text or "derivatives" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "treps" in row_text or "triparty repo" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
            continue

        # ----------------------------
        # SKIP JUNK ROWS  ✅ FIXED
        # ----------------------------

        if (
            company.lower() in [
                "",
                "nan",
                "total",
                "sub total",
                "grand total",
                "listed/awaiting listing on stock exchange",
                "unlisted",
                "notes :"
            ]
            or company.lower().startswith("net current")
        ):
            continue

        # ----------------------------
        # WEIGHT
        # ----------------------------

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        weight = round(weight, 4)

        # ----------------------------
        # ISIN RULES
        # ----------------------------

        if not is_valid_isin(isin):
            isin = None

        if current_section == SECTION_EQUITY and isin is None:
            continue

        # ----------------------------
        # FINAL SECTION  ✅ FIXED
        # ----------------------------

        if is_reit(company, sector):
            section = SECTION_REITS
        elif current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None
        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": company,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)
