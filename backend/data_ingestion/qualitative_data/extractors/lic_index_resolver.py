import pandas as pd
import re

def _normalize(text: str) -> str:
    """
    Normalize scheme names & keywords for robust matching
    """
    text = text.lower()
    text = text.replace("&", "and")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def resolve_lic_sheet(xls_path, fund_keyword):
    """
    LIC Index sheet = Sheet1

    Column A -> Scheme Code
    Column B -> Scheme Name
    """

    keyword = _normalize(fund_keyword)

    index_df = pd.read_excel(xls_path, sheet_name="Sheet1", header=None)

    for _, row in index_df.iterrows():
        if len(row) < 2:
            continue

        scheme_code = str(row.iloc[0]).strip()
        scheme_name = _normalize(str(row.iloc[1]))

        if keyword in scheme_name:
            return scheme_code

    raise ValueError(f"❌ Could not resolve LIC sheet for: {fund_keyword}")
