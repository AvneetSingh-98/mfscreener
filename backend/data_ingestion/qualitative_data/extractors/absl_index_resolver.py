import pandas as pd

def resolve_absl_sheet(xls_path, fund_keyword):
    """
    Resolve actual sheet name using Index sheet
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        fund_code = str(row.iloc[1]).strip()
        fund_name = str(row.iloc[2]).lower()

        if fund_keyword.lower() in fund_name:
            return fund_code

    raise ValueError(f"❌ Could not resolve sheet for: {fund_keyword}")
