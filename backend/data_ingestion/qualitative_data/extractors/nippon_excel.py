import pandas as pd
import math

# =============================
# HELPERS
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
# HEADER DETECTION
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
# INDEX SHEET RESOLVER
# =============================

def resolve_nippon_sheet_code(xls_path, keywords):
    xl = pd.ExcelFile(xls_path)
    index_sheet = next(s for s in xl.sheet_names if "index" in s.lower())
    index_df = pd.read_excel(xls_path, sheet_name=index_sheet, header=None)

    keywords = [normalize_text(k) for k in keywords]

    for _, row in index_df.iterrows():
        if len(row) < 2:
            continue

        code = str(row.iloc[0]).strip()
        name = normalize_text(row.iloc[1])

        if not code.isalnum() or len(code) > 3:
            continue

        # ❌ Reject non-equity
        if any(x in name for x in [
            "liquid", "gilt", "debt", "overnight",
            "etf", "index fund", "gold", "fund of fund"
        ]):
            continue

        if any(k in name for k in keywords):
            return code.upper()

    raise Exception(f"❌ Sheet code not found for keywords: {keywords}")

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

    for _, r in df.iterrows():
        name = str(r[col_map["name"]]).strip()
        if not name:
            continue

        if name.lower().startswith(INVALID_NAME_PREFIXES):
            continue

        isin = str(r[col_map["isin"]]).strip()
        if not is_valid_isin(isin):
            continue

        raw_weight_str = str(r[col_map["weight"]]).replace("%", "").strip()

        try:
            weight = float(raw_weight_str)
        except:
            continue

        if not math.isfinite(weight):
            continue

        # 🔒 NORMALISE
        if 0 < weight < 1:
            weight = weight * 100

        holdings.append({
            "isin": isin,
            "company": name,
            "sector": str(r[col_map["sector"]]).strip(),
            "weight": round(weight, 4)
        })

    return holdings
