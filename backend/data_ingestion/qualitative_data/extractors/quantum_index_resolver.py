import pandas as pd

def resolve_quantum_sheet(xls_path, fund_keyword):
    """
    Quantum Index sheet:
    Col B → Scheme Full Name
    Col C → Scheme Code (sheet name)
    """

    index_df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 3:
            continue

        scheme_name = str(row.iloc[1]).lower()
        scheme_code = str(row.iloc[2]).strip()

        if fund_keyword.lower() in scheme_name:
            return scheme_code

    raise ValueError(f"❌ Could not resolve Quantum sheet for keyword: {fund_keyword}")
