def resolve_kotak_sheet(xls_path, fund_keyword):
    keyword = fund_keyword.lower().strip()

    OVERRIDES = {
        "flexi cap": "SEF",
        "multi cap": "MUC",
        "standard multicap": "MUC",
    }

    if keyword in OVERRIDES:
        return OVERRIDES[keyword]

    # fallback to existing index logic
    import pandas as pd
    df = pd.read_excel(xls_path, sheet_name="Scheme", header=None)

    for _, row in df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[1]):
            continue
        code = str(row[0]).strip()
        name = str(row[1]).lower()
        if keyword in name:
            return code

    raise ValueError(f"❌ Could not resolve Kotak scheme for '{fund_keyword}'")
