import pandas as pd
import re
import math

ISIN_REGEX = re.compile(r"^INE[A-Z0-9]{9}$")

def parse_kotak_portfolio_excel(xls_path, sheet_name):
    df = pd.read_excel(xls_path, sheet_name=sheet_name, header=None)

    # -----------------------------
    # 1️⃣ Find header row
    # -----------------------------
    header_row = None
    for i in range(25):
        row = df.iloc[i].astype(str).str.lower()
        if "name of instrument" in row.values and "isin code" in row.values:
            header_row = i
            break

    if header_row is None:
        raise ValueError(f"❌ Header row not found in {sheet_name}")

    # -----------------------------
    # 2️⃣ Slice data
    # -----------------------------
    data = df.iloc[header_row + 1:].reset_index(drop=True)

    # Fixed Kotak column positions
    COL_COMPANY = 2   # Name of Instrument
    COL_ISIN = 3      # ISIN Code
    COL_SECTOR = 4    # Industry
    COL_WEIGHT = 8    # % to Net Assets

    holdings = []

    # -----------------------------
    # 3️⃣ Parse equity holdings
    # -----------------------------
    for _, row in data.iterrows():
        company = str(row[COL_COMPANY]).strip()
        isin = str(row[COL_ISIN]).strip()
        sector = str(row[COL_SECTOR]).strip()

        # Stop once NAV section starts
        if company.lower().startswith("nav"):
            break

        # Skip non-holding rows
        if company.lower() in [
            "",
            "equity & equity related",
            "listed/awaiting listing on stock exchange",
            "mutual fund units",
            "unlisted",
            "futures",
            "triparty repo",
            "net current assets/(liabilities)",
            "total",
            "grand total",
            "notes :",
        ]:
            continue

        # Only valid Indian equity ISINs
        if not ISIN_REGEX.match(isin):
            continue

        try:
            weight = float(row[COL_WEIGHT])
        except:
            continue

        if math.isnan(weight):
            continue

        holdings.append({
            "isin": isin,
            "company": company,
            "sector": sector,
            "weight": round(weight, 2),
            "weight_num": round(weight, 2),
            "section": "equity"
        })

    # -----------------------------
    # 4️⃣ Section summary
    # -----------------------------
    equity_total = round(sum(h["weight"] for h in holdings), 2)

    top_10_equity = round(
        sum(
            h["weight"]
            for h in sorted(holdings, key=lambda x: x["weight"], reverse=True)[:10]
        ),
        2
    )

    section_summary = {
        "equity": equity_total,
        "top_10_equity": top_10_equity
    }

    return holdings, section_summary
