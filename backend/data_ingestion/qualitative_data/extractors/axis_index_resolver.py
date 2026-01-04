import pandas as pd

def normalize_key(text: str) -> str:
    return (
        text.lower()
        .replace("&", "")
        .replace("and", "")
        .replace(" ", "")
        .strip()
    )

def resolve_axis_sheet(xls_path, fund_keyword):
    """
    Resolve actual sheet name using Index sheet
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    norm_keyword = normalize_key(fund_keyword)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        fund_code = str(row.iloc[1]).strip()
        fund_name = normalize_key(str(row.iloc[2]))

        if norm_keyword in fund_name:
            return fund_code

    raise ValueError(f"❌ Could not resolve sheet for: {fund_keyword}")
