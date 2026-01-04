from pymongo import MongoClient
from extractors.kotak_index_resolver import resolve_kotak_sheet
from extractors.kotak_portfolio_excel import parse_kotak_portfolio_excel

XLS_PATH = r"D:\mfscreener-main\backend\data_ingestion\qualitative_data\factsheets\2025-11\Kotak Mahindra\Kotak_Portfolio.xls"

FUNDS = [
    {"key": "KOTAK_LARGE_CAP", "keyword": "large cap", "category": "Large Cap"},
    {"key": "KOTAK_LARGE_MID_CAP", "keyword": "large & mid", "category": "Large & Mid Cap"},
    {"key": "KOTAK_MID_CAP", "keyword": "midcap", "category": "Mid Cap"},
    {"key": "KOTAK_SMALL_CAP", "keyword": "small cap", "category": "Small Cap"},
    {"key": "KOTAK_FLEXI_CAP", "keyword": "standard multicap", "category": "Flexi Cap"},
    {"key": "KOTAK_MULTI_CAP", "keyword": "multi cap", "category": "Multi Cap"},
    {"key": "KOTAK_CONTRA", "keyword": "contra", "category": "Contra"},
    {"key": "KOTAK_FOCUSED", "keyword": "focused", "category": "Focused"},
    {"key": "KOTAK_ELSS", "keyword": "elss", "category": "ELSS"},
]

client = MongoClient("mongodb://localhost:27017")
db = client["mfscreener"]
col = db["portfolio_holdings_v2"]

for meta in FUNDS:
    print("=" * 60)
    print(f"🚀 Running {meta['key']}")

    sheet = resolve_kotak_sheet(XLS_PATH, meta["keyword"])
    print(f"📄 Sheet resolved : {sheet}")

    holdings, section_summary = parse_kotak_portfolio_excel(XLS_PATH, sheet)

    if not holdings:
        print(f"⚠️ No holdings found for {meta['key']}")
        continue

    doc = {
        "fund_key": meta["key"],
        "amc": "Kotak Mahindra Mutual Fund",
        "as_of": "2025-11-30",
        "asset_class": "Equity",
        "category": meta["category"],
        "counts": {"equity": len(holdings)},
        "holdings": holdings,
        "section_summary": section_summary
    }

    col.replace_one(
        {"fund_key": meta["key"], "as_of": "2025-11-30"},
        doc,
        upsert=True
    )

    print(f"✅ Done: {meta['key']} | Holdings = {len(holdings)}")
