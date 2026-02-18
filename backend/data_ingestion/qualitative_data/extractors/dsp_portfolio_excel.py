import pandas as pd
import math
from collections import defaultdict

# =====================================================
# SECTIONS
# =====================================================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

INVALID_PREFIXES = (
    "sub total",
    "total",
    "grand total",
    "net",
    "portfolio classification",
)

# =====================================================
# HELPERS
# =====================================================

def is_valid_isin(val):
    if not val:
        return False
    val = str(val).strip().upper()
    return len(val) == 12 and val.isalnum()


def normalize(x):
    return str(x).lower().strip()

def find_header_row(df):
    for i in range(len(df)):
        row_text = " ".join(
            str(x).lower() for x in df.iloc[i].values if pd.notna(x)
        )

        if (
            "name of instrument" in row_text
            and "isin" in row_text
            and (
                "% to net" in row_text
                or "% of net" in row_text
                or "net assets" in row_text
            )
        ):
            return i

    return None


def detect_percent_column(df, start_col, start_row):
    best_col = None
    best_score = 0

    for c in range(start_col, min(start_col + 7, df.shape[1])):
        s = pd.to_numeric(df.iloc[start_row:, c], errors="coerce").dropna()
        if len(s) < 10:
            continue
        score = ((s > 0) & (s <= 1)).mean()
        if score > best_score:
            best_score = score
            best_col = c

    if best_col is None:
        raise Exception("❌ Could not detect % column")

    return best_col

def is_reit(name, sector):
    t = f"{name} {sector}".lower()
    return any(x in t for x in ["reit", "invit", "real estate investment trust"])

# =====================================================
# MAIN PARSER
# =====================================================

def parse_dsp_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header not found in sheet: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("instrument", case=False)].index[0]
    COL_ISIN   = header[header.str.contains("isin", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry|sector|rating", case=False)].index[0]

    COL_WEIGHT = detect_percent_column(df, COL_NAME + 1, header_row + 1)

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =================================================
    # ROW LOOP
    # =================================================

    for i in range(header_row + 1, len(df)):

        row = df.iloc[i]
        row_text = " ".join(normalize(x) for x in row.values if pd.notna(x))

        # ---------------- SECTION SWITCHING ----------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if (
            "alternative investment fund" in row_text
            or "mutual fund units" in row_text
            or "exchange traded funds" in row_text
            or "etf" in row_text
        ):
            current_section = SECTION_OTHERS
            continue

        if "debt instruments" in row_text or "money market instruments" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "margin (future" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("invit")
            or "real estate investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        if current_section is None:
            current_section = SECTION_OTHERS

        # ---------------- DATA EXTRACTION ----------------

        name = row[COL_NAME]
        isin = row[COL_ISIN]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(name) or pd.isna(weight_raw):
            continue

        name = str(name).strip()
        if normalize(name).startswith(INVALID_PREFIXES):
            continue

        if current_section == SECTION_EQUITY and not is_valid_isin(isin):
            continue

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        if not math.isfinite(weight):
            continue

        

        weight = round(weight, 4)

        sector = str(sector).strip() if pd.notna(sector) else ""

        # Final section override
        if is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": str(isin).strip() if is_valid_isin(isin) else None,
            "company": name,
            "sector": sector,
            "weight": weight,
            "weight_num": weight,
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

