import pandas as pd

def normalize(text: str) -> str:
    return (
        text.lower()
        .replace("&", " ")
        .replace("and", " ")
        .replace("-", " ")
        .strip()
    )

def tokenize(text: str):
    return set(normalize(text).split())

def resolve_baroda_sheet(xls_path, fund_keyword):
    """
    Resolve Baroda BNP Paribas scheme sheet using Index
    (token-based, collision-safe)
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    keyword_tokens = tokenize(fund_keyword)
    candidates = []

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        scheme_code = str(row.iloc[1]).strip()   # Short Name (TOME04)
        scheme_name = str(row.iloc[2])

        scheme_tokens = tokenize(scheme_name)

        if keyword_tokens.issubset(scheme_tokens):
            candidates.append((scheme_code, scheme_name))

    if not candidates:
        raise ValueError(f"❌ Could not resolve Baroda sheet for: {fund_keyword}")

    # Pick most specific (shortest name)
    candidates.sort(key=lambda x: len(x[1]))

    return candidates[0][0]
