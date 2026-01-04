import pandas as pd

INVALID_PREFIXES = (
    "equity",
    "listed",
    "awaiting",
    "subtotal",
    "total",
    "grand total",
    "money market",
    "treps",
    "repo",
    "reverse repo",
    "net receivable",
    "payable",
    "accrued",
)

def normalize(text):
    return str(text).lower().replace("\n", " ").strip()

def find_header_row(df):
    for i in range(30):
        row = df.iloc[i].astype(str).str.lower()
        joined = " ".join(row.values)
        if "isin" in joined and "% to net" in joined:
            return i
    return None

def find_col(columns, keywords):
    for col in columns:
        name = normalize(col)
        for kw in keywords:
            if kw in name:
                return col
    return None

def is_valid_isin(val):
    return isinstance(val, str) and val.strip().upper().startswith("INE")

def is_noise_company(name):
    name = normalize(name)
    return any(k in name for k in INVALID_PREFIXES)

def parse_mirae_portfolio(xls_path, sheet_name):
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    header_row = find_header_row(df)
    if header_row is None:
        raise ValueError("❌ Could not detect header row")

    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    col_company = find_col(df.columns, ["name"])
    col_isin = find_col(df.columns, ["isin"])
    col_sector = find_col(df.columns, ["industry", "sector"])
    col_weight = find_col(df.columns, ["% to net"])

    if not col_company or not col_isin or not col_weight:
        raise ValueError("❌ Required columns missing")

    holdings = []

    for _, row in df.iterrows():
        isin = str(row[col_isin]).strip()

        if not is_valid_isin(isin):
            continue

        company = str(row[col_company]).strip()
        if is_noise_company(company):
            continue

        try:
            weight = float(row[col_weight])
        except:
            continue

        if weight <= 0:
            continue

        holdings.append({
            "isin": isin,
            "company": company,
            "sector": str(row[col_sector]).strip() if col_sector else None,
            "weight": round(weight, 6),
            "weight_num": round(weight, 6),
            "section": "equity"
        })

    return holdings
