# backend/data_ingestion/qualitative_data/extractors/samco_fund_registry.py

SAMCO_FUND_REGISTRY = {

    # =========================
    # Equity – Core
    # =========================

    "SAMCO_LARGE_CAP": {
        "category": "Large Cap",
        "asset_class": "Equity",
        "sheet": "Large Cap Fund"
    },

    "SAMCO_LARGE_MID_CAP": {
        "category": "Large & Mid Cap",
        "asset_class": "Equity",
        "sheet": "Large & Mid Cap Fund"
    },

    "SAMCO_FLEXI_CAP": {
        "category": "Flexi Cap",
        "asset_class": "Equity",
        "sheet": "Flexi Cap Fund"
    },

    "SAMCO_MULTI_CAP": {
        "category": "Multi Cap",
        "asset_class": "Equity",
        "sheet": "Multi Cap Fund"
    },

    "SAMCO_SMALL_CAP": {
        "category": "Small Cap",
        "asset_class": "Equity",
        "sheet": "Small Cap Fund"
    },

    "SAMCO_ELSS": {
        "category": "ELSS",
        "asset_class": "Equity",
        "sheet": "ELSS Tax Saver Fund"
    },

    # =========================
    # Equity – Thematic
    # =========================

    "SAMCO_ACTIVE_MOMENTUM": {
        "category": "Active Momentum",
        "asset_class": "Equity",
        "sheet": "Active Momentum Fund"
    },

    "SAMCO_SPECIAL_OPPORTUNITIES": {
        "category": "Special Opportunities",
        "asset_class": "Equity",
        "sheet": "Special Opportunities Fund"
    },

    # =========================
    # Hybrid / Allocation
    # =========================

    "SAMCO_DYNAMIC_ASSET_ALLOCATION": {
        "category": "Dynamic Asset Allocation",
        "asset_class": "Hybrid",
        "sheet": "Dynamic Asset Allocation Fund"
    },

    "SAMCO_MULTI_ASSET": {
        "category": "Multi Asset Allocation",
        "asset_class": "Hybrid",
        "sheet": "Multi Asset Allocation Fund"
    }

}
