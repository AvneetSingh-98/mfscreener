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

def resolve_boi_sheet(xls_path, fund_keyword):
    """
    Resolve BOI scheme sheet using Index sheet
    with priority-safe category matching
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    keyword_tokens = tokenize(fund_keyword)

    candidates = []

    for _, row in index_df.iterrows():
        if len(row) < 2:
            continue

        scheme_code = str(row.iloc[0]).strip()
        scheme_name_raw = str(row.iloc[1])

        scheme_tokens = tokenize(scheme_name_raw)

        # ✅ FULL TOKEN MATCH (not substring)
        if keyword_tokens.issubset(scheme_tokens):
            candidates.append((scheme_code, scheme_name_raw))

    if not candidates:
        raise ValueError(f"❌ Could not resolve BOI sheet for: {fund_keyword}")

    # ✅ If multiple matches, pick the SHORTEST name (most specific)
    candidates.sort(key=lambda x: len(x[1]))

    return candidates[0][0]
