import pandas as pd

def resolve_edelweiss_sheet(xls_path, sheet_code):
    xls = pd.ExcelFile(xls_path)

    for sheet in xls.sheet_names:
        if sheet.strip().upper() == sheet_code.upper():
            return sheet

    raise Exception(f"❌ Sheet not found for code: {sheet_code}")
