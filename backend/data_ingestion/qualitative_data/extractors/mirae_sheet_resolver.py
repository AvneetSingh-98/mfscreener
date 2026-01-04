import pandas as pd

def normalize(text):
    return str(text).lower().strip()

def resolve_mirae_sheet(xls_path, sheet_name):
    xls = pd.ExcelFile(xls_path)

    for sheet in xls.sheet_names:
        if normalize(sheet) == normalize(sheet_name):
            return sheet

    raise ValueError(f"❌ Sheet not found in Mirae Excel: {sheet_name}")
