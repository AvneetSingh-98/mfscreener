import pandas as pd
import re

def _norm(text: str) -> str:
    """
    Aggressive normalization for Motilal index matching
    """
    text = str(text).lower()
    text = re.sub(r"\(.*?\)", "", text)      # remove (formerly known as ...)
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def resolve_motilal_sheet(xls_path, fund_code):
    """
    Motilal sheets are ALWAYS fund-code based (YOxx)
    """
    return fund_code
