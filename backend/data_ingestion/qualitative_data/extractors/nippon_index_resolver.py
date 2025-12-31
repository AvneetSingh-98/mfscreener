import pandas as pd
import re

def _normalize(text: str) -> str:
    text = str(text).upper()
    text = re.sub(r"\(.*?\)", " ", text)   # remove bracketed text
    text = re.sub(r"[^A-Z ]", " ", text)   # remove symbols
    text = re.sub(r"\s+", " ", text)       # collapse spaces
    return text.strip()


def build_index_map(xls_path):
    index_df = pd.read_excel(
        xls_path,
        sheet_name="Index",
        header=None
    )

    index_map = []

    for _, row in index_df.iterrows():
        if pd.isna(row[0]) or pd.isna(row[1]):
            continue

        sheet_code = str(row[0]).strip()
        name_raw = str(row[1])

        normalized_name = _normalize(name_raw)

        index_map.append({
            "sheet": sheet_code,
            "name": normalized_name
        })

    return index_map


def resolve_sheet_code(index_map, canonical_name):
    canonical = _normalize(canonical_name)

    # 1️⃣ STRICT EXACT MATCH (THIS FIXES LARGE CAP)
    for row in index_map:
        if row["name"] == canonical:
            return row["sheet"]

    # 2️⃣ FALLBACK ONLY IF NO EXACT MATCH EXISTS
    canonical_tokens = canonical.split()

    EXCLUDE_TOKENS = [
        "FUND OF FUND",
        "FOF",
        "PASSIVE",
        "ETF",
        "INDEX",
        "BEES"
    ]

    for row in index_map:
        row_name = row["name"]

        if any(x in row_name for x in EXCLUDE_TOKENS):
            continue

        if all(tok in row_name for tok in canonical_tokens):
            return row["sheet"]

    raise Exception(f"❌ Sheet code not found in Index for: {canonical_name}")


    
