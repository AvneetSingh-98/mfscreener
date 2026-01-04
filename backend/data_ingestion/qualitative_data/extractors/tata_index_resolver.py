import pandas as pd

def resolve_tata_sheet(xls_path, fund_key, keyword=None):
    """
    Tata resolver:
    - Use scheme code ONLY for MULTI CAP
    - All others resolved via Index keyword
    """

    # ✅ Special case: Multi Cap
    if fund_key == "TATA_MULTI_CAP":
        return "TMULTICF"

    # ✅ Normal case: keyword-based resolution
    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        scheme_code = str(row.iloc[1]).strip()
        scheme_name = str(row.iloc[2]).lower()

        if keyword and keyword.lower() in scheme_name:
            return scheme_code

    raise ValueError(f"❌ Could not resolve Tata sheet for {fund_key}")

