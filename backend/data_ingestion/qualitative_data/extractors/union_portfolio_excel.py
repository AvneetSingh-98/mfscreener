import pandas as pd
import math
from collections import defaultdict

# =========================
# SECTIONS
# =========================

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
    "net current",
    "portfolio classification",
)

# =========================
# HELPERS
# =========================

def normalize(x):
    return str(x).lower().strip()

def is_valid_isin(text):
    if not text:
        return False
    text = str(text).strip().upper()
    return len(text) == 12 and text.isalnum()

def extract_name_isin(raw):
    raw = str(raw).strip()
    parts = raw.split()
    isin = next((p for p in parts if is_valid_isin(p)), None)
    name = raw.replace(isin, "").strip() if isin else raw
    return name, isin

def find_isin_anywhere(row):
    for val in row.values:
        if is_valid_isin(val):
            return str(val).strip()
    return None

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust"
    ])

# =========================
# HEADER DETECTION
# =========================

def find_header_row(df):
    for i in range(len(df)):
        text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "name of the instrument" in text and "% to nav" in text:
            return i
    return None

# =========================
# PERCENT COLUMN DETECTION
# =========================

def detect_percent_column(df, qty_col_idx, start_row):
    best_col = None
    best_score = 0.0

    for col_idx in range(qty_col_idx + 1, min(qty_col_idx + 6, df.shape[1])):
        series = pd.to_numeric(
            df.iloc[start_row:, col_idx],
            errors="coerce"
        ).dropna()

        if len(series) < 10:
            continue

        score = ((series > 0) & (series <= 100)).mean()
        if score > best_score:
            best_score = score
            best_col = col_idx

    if best_col is None:
        raise Exception("❌ Could not detect % to NAV column")

    return best_col

# =========================
# MAIN PARSER
# =========================

def parse_union_portfolio_excel(xls_path, sheet_name):

    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise Exception(f"❌ Header row not found: {sheet_name}")

    header = df.iloc[header_row].astype(str)

    COL_NAME   = header[header.str.contains("name", case=False)].index[0]
    COL_SECTOR = header[header.str.contains("industry", case=False)].index[0]
    COL_QTY    = header[header.str.contains("quantity", case=False)].index[0]

    COL_WEIGHT = detect_percent_column(df, COL_QTY, header_row + 1)

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY

    # =========================
    # ROW LOOP
    # =========================

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]

        row_text = " ".join(
            normalize(x) for x in row.values if pd.notna(x)
        )

        # ---------- SECTION SWITCH (same as Canara) ----------
        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue

        if "exchange traded funds" in row_text:
            current_section = SECTION_OTHERS
            continue

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

        if "derivative" in row_text or "margin (future" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if (
            row_text.startswith("reit")
            or row_text.startswith("reits")
            or row_text.startswith("invit")
            or "real estate investment trust" in row_text
        ):
            current_section = SECTION_REITS
            continue

        if current_section is None:
            current_section = SECTION_OTHERS

        # ---------- DATA ----------
        raw_name = row[COL_NAME]
        sector = row[COL_SECTOR]
        weight_raw = row[COL_WEIGHT]

        if pd.isna(raw_name) or pd.isna(weight_raw):
            continue

        raw_name = str(raw_name).strip()
        lname = normalize(raw_name)
        if any(x in lname for x in INVALID_PREFIXES):
            continue

        name, isin = extract_name_isin(raw_name)

        if not isin:
            isin = find_isin_anywhere(row)

        if current_section == SECTION_EQUITY and not isin:
            continue

        sector = str(sector).strip() if pd.notna(sector) else ""

        try:
            weight = float(str(weight_raw).replace("%", "").strip())
        except:
            continue

        # Union gives % already
        if not math.isfinite(weight) or not (0 < weight <= 100):
            continue

        weight = round(weight, 4)

        # ---------- FINAL SECTION ----------
        if current_section == SECTION_DERIVATIVES:
            section = SECTION_DERIVATIVES
            isin = None
        elif is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin,
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
