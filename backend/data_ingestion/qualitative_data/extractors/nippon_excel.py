import pandas as pd
import math
from collections import defaultdict

# =============================
# SECTIONS
# =============================

SECTION_EQUITY = "equity"
SECTION_DEBT = "debt"
SECTION_REITS = "reits"
SECTION_DERIVATIVES = "derivatives"
SECTION_CASH = "cash"
SECTION_OTHERS = "others"

# =============================
# HELPERS (UNCHANGED)
# =============================

def normalize(text):
    return str(text).lower().strip()

def normalize_text(text):
    text = str(text).lower()
    text = text.replace("\n", " ")
    return " ".join(text.split())

def is_valid_isin(isin: str) -> bool:
    if not isin:
        return False
    isin = str(isin).strip().upper()
    if isin in ("NIL", "NA", "NONE", "NAN"):
        return False
    return len(isin) == 12 and isin.isalnum()

# =============================
# HEADER DETECTION (UNCHANGED)
# =============================

def find_header_row(df):
    for i in range(40):
        row = [normalize(x) for x in df.iloc[i].tolist()]
        if (
            any("name of the instrument" in x for x in row)
            and any("% to nav" in x for x in row)
        ):
            return i
    raise Exception("❌ Header row not found")

# =============================
# REIT DETECTOR
# =============================

def is_reit(name, sector):
    text = f"{name} {sector}".lower()
    return any(x in text for x in [
        "reit",
        "invit",
        "real estate investment trust",
        "infrastructure investment trust"
    ])

# =============================
# MAIN PARSER
# =============================

REQUIRED_COLS = {
    "isin": ["isin"],
    "name": ["name of the instrument"],
    "sector": ["industry"],
    "weight": ["% to nav"]
}

INVALID_NAME_PREFIXES = (
    "equity & equity",
    "listed / awaiting",
    "total",
    "sub total",
    "grand total",
    "scheme risk",
    "net current assets",
    "subtotal",
)

def parse_nippon_sheet(xls_path, sheet_code):

    raw = pd.read_excel(xls_path, sheet_name=sheet_code, header=None)
    header_row = find_header_row(raw)

    df = pd.read_excel(
        xls_path,
        sheet_name=sheet_code,
        header=header_row
    )

    df.columns = [normalize(c) for c in df.columns]

    col_map = {}
    for k, variants in REQUIRED_COLS.items():
        for c in df.columns:
            if any(v in c for v in variants):
                col_map[k] = c
                break

    if set(col_map.keys()) != set(REQUIRED_COLS.keys()):
        raise Exception(f"❌ Required columns missing\nFound: {list(df.columns)}")

    holdings = []
    section_summary = defaultdict(list)

    current_section = SECTION_EQUITY   # Nippon sheets start with equity

    # =============================
    # ROW LOOP
    # =============================

    for _, r in df.iterrows():

        row_text = " ".join(
            normalize(x) for x in r.values if pd.notna(x)
        )

        # -------------------------
        # SECTION SWITCHING
        # -------------------------

        if "equity & equity related" in row_text:
            current_section = SECTION_EQUITY
            continue
        if "exchange traded funds" in row_text:
          current_section = SECTION_OTHERS
          continue

        if "etf" in row_text:
          current_section = SECTION_OTHERS
        if "debt instruments" in row_text or "money market" in row_text:
            current_section = SECTION_DEBT
            continue

        if "treps" in row_text or "reverse repo" in row_text:
            current_section = SECTION_CASH
            continue

        # ✅ NEW
        if "net receivable" in row_text or "net payable" in row_text:
            current_section = SECTION_CASH
            continue

        if "derivatives" in row_text or "futures" in row_text:
            current_section = SECTION_DERIVATIVES
            continue

        if "mutual fund units" in row_text:
            current_section = SECTION_OTHERS
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

        # -------------------------
        # DATA EXTRACTION
        # -------------------------

        name = str(r[col_map["name"]]).strip()
        if not name:
            continue

        if name.lower().startswith(INVALID_NAME_PREFIXES):
            continue

        isin = str(r[col_map["isin"]]).strip()

        raw_weight_str = str(r[col_map["weight"]]).replace("%", "").strip()

        try:
            weight = float(raw_weight_str)
        except:
            continue

        if not math.isfinite(weight):
            continue

        # 🔒 Normalize fractional values
        if 0 < weight < 1:
            weight = weight * 100

        # -------------------------
        # ISIN RULE (TWEAKED)
        # -------------------------

        if current_section in (SECTION_EQUITY, SECTION_DEBT):
            if not is_valid_isin(isin):
                continue
        else:
            isin = None

        sector = str(r[col_map["sector"]]).strip()

        # -------------------------
        # FINAL SECTION OVERRIDE
        # -------------------------

        if is_reit(name, sector):
            section = SECTION_REITS
        else:
            section = current_section

        holding = {
            "isin": isin,
            "company": name,
            "sector": sector,
            "weight": round(weight, 4),
            "weight_num": round(weight, 4),
            "section": section
        }

        idx = len(holdings)
        holdings.append(holding)
        section_summary[section].append(idx)

    return holdings, dict(section_summary)

