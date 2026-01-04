import pandas as pd

def resolve_sundaram_sheet(xls_path, fund_keyword):
    """
    Resolve sheet using Index sheet (ABSL-style)
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        scheme_name = str(row.iloc[2]).lower()
        sheet_code = str(row.iloc[1]).strip()

        if fund_keyword in scheme_name:
            return sheet_code

    raise ValueError(f"❌ Could not resolve Sundaram sheet for keyword: {fund_keyword}")
