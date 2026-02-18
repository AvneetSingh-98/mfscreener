# backend/data_ingestion/qualitative_data/extractors/quantum_fund_registry.py

QUANTUM_FUND_REGISTRY = {

    "QUANTUM_VALUE": {
        "category": "Value",
        "asset_class": "Equity",
        "sheet": "QLTEVF"
    },

    "QUANTUM_ELSS": {
        "category": "ELSS",
        "asset_class": "Equity",
        "sheet": "QTSF"
    },

    "QUANTUM_SMALL_CAP": {
        "category": "Small Cap",
        "asset_class": "Equity",
        "sheet": "QSCAPF"
    },

    "QUANTUM_ESG": {
        "category": "ESG",
        "asset_class": "Equity",
        "sheet": "QESG"
    },

    "QUANTUM_ETHICAL": {
        "category": "Ethical",
        "asset_class": "Equity",
        "sheet": "QETHICAL"
    },

    "QUANTUM_MULTI_ASSET": {
        "category": "Multi Asset Allocation",
        "asset_class": "Hybrid",
        "sheet": "QMULTI"
    }

}
