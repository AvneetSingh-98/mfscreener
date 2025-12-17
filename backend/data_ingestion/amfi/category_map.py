AMFI_CATEGORY_MAP = {
    # ===== DEBT =====
    "Overnight": {"asset_class": "Debt"},
    "Liquid": {"asset_class": "Debt"},
    "Ultra Short Duration": {"asset_class": "Debt"},
    "Low Duration": {"asset_class": "Debt"},
    "Short Duration": {"asset_class": "Debt"},
    "Medium Duration": {"asset_class": "Debt"},
    "Medium to Long Duration": {"asset_class": "Debt"},
    "Long Duration": {"asset_class": "Debt"},
    "Dynamic Bond": {"asset_class": "Debt"},
    "Corporate Bond": {"asset_class": "Debt"},
    "Credit Risk": {"asset_class": "Debt"},
    "Banking and PSU": {"asset_class": "Debt"},
    "Gilt": {"asset_class": "Debt"},
    "Gilt with 10 year constant duration": {"asset_class": "Debt"},
    "Floater": {"asset_class": "Debt"},
    "Money Market": {"asset_class": "Debt"},
    "FMP": {"asset_class": "Debt"},

    # ===== EQUITY =====
    "Large Cap": {"asset_class": "Equity"},
    "Large & Mid Cap": {"asset_class": "Equity"},
    "Flexi Cap": {"asset_class": "Equity"},
    "Multi Cap": {"asset_class": "Equity"},
    "Mid Cap": {"asset_class": "Equity"},
    "Small Cap": {"asset_class": "Equity"},
    "Value": {"asset_class": "Equity"},
    "ELSS": {"asset_class": "Equity"},
    "Contra": {"asset_class": "Equity"},
    "Dividend Yield": {"asset_class": "Equity"},
    "Focused": {"asset_class": "Equity"},
    "Sectoral / Thematic": {"asset_class": "Equity"},

    # ===== HYBRID =====
    "Aggressive Hybrid": {"asset_class": "Hybrid"},
    "Conservative Hybrid": {"asset_class": "Hybrid"},
    "Balanced Hybrid": {"asset_class": "Hybrid"},
    "Arbitrage": {"asset_class": "Hybrid"},
    "Equity Savings": {"asset_class": "Hybrid"},
    "Dynamic Asset Allocation or Balanced Advantage": {"asset_class": "Hybrid"},
    "Multi Asset Allocation": {"asset_class": "Hybrid"},

    # ===== SOLUTION =====
    "Retirement": {"asset_class": "Solution Oriented"},
    "Children": {"asset_class": "Solution Oriented"},

    # ===== OTHER =====
    "Index Funds ETFs": {"asset_class": "Other"},
    "FoFs (Overseas/Domestic)": {"asset_class": "Other"}
}
def normalize_category(category_raw: str):
    """
    Converts AMFI category header into:
    asset_class + normalized category
    """
    if not category_raw:
        return "Unknown", "Unknown"

    raw = category_raw.lower()

    for category_key, meta in AMFI_CATEGORY_MAP.items():
        if category_key.lower() in raw:
            return meta["asset_class"], category_key

    return "Unknown", "Unknown"
