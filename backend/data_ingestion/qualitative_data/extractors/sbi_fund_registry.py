# backend/data_ingestion/qualitative_data/extractors/sbi_fund_registry.py

SBI_FUND_REGISTRY = {

    # =========================
    # Equity – Core
    # =========================

    "SBI_LARGE_CAP": {
        "category": "Large Cap",
        "asset_class": "Equity",
        "sheet": "SBLUECHIP"
    },

    "SBI_LARGE_MID_CAP": {
        "category": "Large & Mid Cap",
        "asset_class": "Equity",
        "sheet": "SLMF"
    },

    "SBI_MID_CAP": {
        "category": "Mid Cap",
        "asset_class": "Equity",
        "sheet": "SMIDCAP"
    },

    "SBI_SMALL_CAP": {
        "category": "Small Cap",
        "asset_class": "Equity",
        "sheet": "SSCF"
    },

    "SBI_FLEXI_CAP": {
        "category": "Flexi Cap",
        "asset_class": "Equity",
        "sheet": "SFLEXI"
    },

    "SBI_MULTI_CAP": {
        "category": "Multi Cap",
        "asset_class": "Equity",
        "sheet": "SMCF"
    },

    "SBI_ELSS": {
        "category": "ELSS",
        "asset_class": "Equity",
        "sheet": "SLTEF"
    },

    "SBI_FOCUSED": {
        "category": "Focused",
        "asset_class": "Equity",
        "sheet": "SFEF"
    },

    # =========================
    # Equity – Styles / Factors
    # =========================

    "SBI_CONTRA": {
        "category": "Contra",
        "asset_class": "Equity",
        "sheet": "SCF"
    },

    "SBI_DIVIDEND_YIELD": {
        "category": "Dividend Yield",
        "asset_class": "Equity",
        "sheet": "SDYF"
    },

    "SBI_MIN_VARIANCE": {
        "category": "Minimum Variance",
        "asset_class": "Equity",
        "sheet": "SEMVF"
    },

    "SBI_QUANT": {
        "category": "Quant",
        "asset_class": "Equity",
        "sheet": "SQF"
    },

    "SBI_MNC": {
        "category": "MNC",
        "asset_class": "Equity",
        "sheet": "SMGLF"
    },

    "SBI_ESG": {
        "category": "ESG",
        "asset_class": "Equity",
        "sheet": "SMEEF"
    },

    # =========================
    # Equity – Sectoral / Thematic
    # =========================

    "SBI_CONSUMPTION": {
        "category": "Consumption",
        "asset_class": "Equity",
        "sheet": "SCOF"
    },

    "SBI_TECHNOLOGY": {
        "category": "Technology",
        "asset_class": "Equity",
        "sheet": "STOF"
    },

    "SBI_HEALTHCARE": {
        "category": "Healthcare",
        "asset_class": "Equity",
        "sheet": "SHOF"
    },

    "SBI_INFRASTRUCTURE": {
        "category": "Infrastructure",
        "asset_class": "Equity",
        "sheet": "SIF"
    },

    "SBI_PSU": {
        "category": "PSU",
        "asset_class": "Equity",
        "sheet": "SPSU"
    },

    "SBI_BANKING_PSU": {
        "category": "Banking & PSU",
        "asset_class": "Equity",
        "sheet": "SBPF"
    },

    "SBI_BANKING_FINANCIAL": {
        "category": "Banking & Financial Services",
        "asset_class": "Equity",
        "sheet": "SBFS"
    },

    "SBI_ENERGY": {
        "category": "Energy",
        "asset_class": "Equity",
        "sheet": "SEOF"
    },

    "SBI_AUTOMOTIVE": {
        "category": "Automotive",
        "asset_class": "Equity",
        "sheet": "SBI-AOF"
    },

    "SBI_INNOVATIVE_OPPORTUNITIES": {
        "category": "Innovative Opportunities",
        "asset_class": "Equity",
        "sheet": "SIOF"
    },

    "SBI_RESURGENT_INDIA": {
        "category": "Special Opportunities",
        "asset_class": "Equity",
        "sheet": "SBIRIOS"
    },

    # =========================
    # Hybrid
    # =========================

    "SBI_EQUITY_HYBRID": {
        "category": "Aggressive Hybrid",
        "asset_class": "Hybrid",
        "sheet": "SEHF"
    },

    "SBI_CONSERVATIVE_HYBRID": {
        "category": "Conservative Hybrid",
        "asset_class": "Hybrid",
        "sheet": "SCHF"
    },

    "SBI_ARBITRAGE": {
        "category": "Arbitrage",
        "asset_class": "Hybrid",
        "sheet": "SAOF"
    },

    "SBI_EQUITY_SAVINGS": {
        "category": "Equity Savings",
        "asset_class": "Hybrid",
        "sheet": "SESF"
    },

    "SBI_MULTI_ASSET": {
        "category": "Multi Asset Allocation",
        "asset_class": "Hybrid",
        "sheet": "SMAAF"
    },

    "SBI_BALANCED_ADVANTAGE": {
        "category": "Balanced Advantage",
        "asset_class": "Hybrid",
        "sheet": "SBAF"
    },

    "SBI_RETIREMENT_AGGRESSIVE": {
        "category": "Retirement Aggressive",
        "asset_class": "Hybrid",
        "sheet": "SRBF-AP"
    },

    "SBI_RETIREMENT_AGGRESSIVE_HYBRID": {
        "category": "Retirement Aggressive Hybrid",
        "asset_class": "Hybrid",
        "sheet": "SRBF-AHP"
    },

    "SBI_RETIREMENT_CONSERVATIVE_HYBRID": {
        "category": "Retirement Conservative Hybrid",
        "asset_class": "Hybrid",
        "sheet": "SRBF-CHP"
    },

    "SBI_RETIREMENT_CONSERVATIVE": {
        "category": "Retirement Conservative",
        "asset_class": "Hybrid",
        "sheet": "SRBF-CP"
    }

}
