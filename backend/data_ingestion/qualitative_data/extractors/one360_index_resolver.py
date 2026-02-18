import pandas as pd

def resolve_one360_sheet(xls_path, fund_keyword):
    """
    Resolve 360 ONE sheet by scanning sheet content
    (fund name present inside sheet, not tab name)
    """
    xls = pd.ExcelFile(xls_path)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls_path, sheet_name=sheet, nrows=15, header=None)

        text = " ".join(
            str(x).lower()
            for row in df.values
            for x in row
            if pd.notna(x)
        )

        if fund_keyword.lower() in text:
            return sheet

    raise ValueError(f"❌ Could not resolve 360 ONE sheet for keyword: {fund_keyword}")
