import pdfplumber
from collections import defaultdict

SECTION_EQUITY = "equity"

STOP_ROWS = (
    "preference shares",
    "cash equivalent",
    "treps",
    "net current assets",
    "total net assets",
)

def is_holdings_header(header):
    header = [h.lower() for h in header if h]
    return (
        "issuer" in header
        and "industry" in header
        and "% to net assets" in header[-1]
    )

def parse_hsbc_factsheet(pdf_path, fund_title):

    holdings = []
    section_summary = defaultdict(list)

    with pdfplumber.open(pdf_path) as pdf:

        fund_page_idx = None

        # --------------------------------------------------
        # 1️⃣ Find fund title page
        # --------------------------------------------------
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if fund_title.lower() in text.lower():
                fund_page_idx = i
                break

        if fund_page_idx is None:
            raise Exception(f"❌ Fund title not found: {fund_title}")

        # --------------------------------------------------
        # 2️⃣ Scan next pages for holdings table
        # --------------------------------------------------
        for page_idx in range(fund_page_idx, min(fund_page_idx + 5, len(pdf.pages))):

            page = pdf.pages[page_idx]
            tables = page.extract_tables() or []

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header = [str(x).strip() if x else "" for x in table[0]]

                if not is_holdings_header(header):
                    continue

                # --------------------------------------------------
                # 3️⃣ Parse holdings rows
                # --------------------------------------------------
                for row in table[1:]:

                    if not row or len(row) < 3:
                        continue

                    issuer = (row[0] or "").strip()
                    industry = (row[1] or "").strip()
                    weight_raw = (row[-1] or "").strip()

                    if not issuer:
                        continue

                    if issuer.lower().startswith("equity"):
                        continue

                    if any(x in issuer.lower() for x in STOP_ROWS):
                        return holdings, dict(section_summary)

                    try:
                        weight = float(weight_raw.replace("%", "").strip())
                    except:
                        continue

                    holding = {
                        "isin": None,
                        "company": issuer,
                        "sector": industry,
                        "weight": weight,
                        "weight_num": weight,
                        "section": SECTION_EQUITY
                    }

                    idx = len(holdings)
                    holdings.append(holding)
                    section_summary[SECTION_EQUITY].append(idx)

        return holdings, dict(section_summary)
