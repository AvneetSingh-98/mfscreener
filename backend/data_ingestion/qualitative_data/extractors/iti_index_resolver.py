import pandas as pd

def resolve_iti_sheet(xls_path, fund_keyword):
    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        sheet_code = str(row.iloc[1]).strip()
        scheme_name = str(row.iloc[2]).lower()

        if fund_keyword.lower() in scheme_name:
            return sheet_code

    raise ValueError(f"❌ Could not resolve sheet for: {fund_keyword}")
