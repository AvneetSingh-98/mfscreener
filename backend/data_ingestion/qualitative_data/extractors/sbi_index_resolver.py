import pandas as pd
import re

def normalize(text):
    return str(text).lower().strip()

def compact(text):
    """
    Remove spaces & non-alphanumerics for fuzzy-but-safe matching
    """
    return re.sub(r"[^a-z0-9]", "", normalize(text))

def resolve_sbi_sheet(xls_path: str, scheme_keyword: str) -> str:
    """
    Robust SBI Index resolver (final)
    """

    df = pd.read_excel(xls_path, sheet_name="Index", header=None)

    # -------------------------------------------------
    # Find header row
    # -------------------------------------------------
    header_row = None
    for i in range(len(df)):
        row_text = " ".join(
            normalize(x) for x in df.iloc[i].values if pd.notna(x)
        )
        if "scheme" in row_text and "code" in row_text:
            header_row = i
            break

    if header_row is None:
        raise Exception("❌ SBI Index header row not found")

    header = df.iloc[header_row].apply(normalize)

    try:
        COL_CODE = header[
            header.str.contains("short") & header.str.contains("code")
        ].index[0]

        COL_NAME = header[
            header.str.contains("scheme") & header.str.contains("name")
        ].index[0]

    except IndexError:
        raise Exception(f"❌ SBI Index columns not detected: {list(header)}")

    # -------------------------------------------------
    # Keyword match (space-insensitive)
    # -------------------------------------------------
    kw = compact(scheme_keyword)

    for i in range(header_row + 1, len(df)):
        row = df.iloc[i]
        name = row[COL_NAME]

        if pd.isna(name):
            continue

        if kw in compact(name):
            return str(row[COL_CODE]).strip()

    raise Exception(f"❌ SBI scheme not found in Index for keyword: {scheme_keyword}")
