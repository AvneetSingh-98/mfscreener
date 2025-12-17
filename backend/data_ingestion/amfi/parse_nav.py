from datetime import datetime
import re


def clean_scheme_code(raw_code: str):
    if not raw_code:
        return None
    return re.sub(r"[^\d]", "", raw_code)


def parse_amfi_nav(raw_lines):
    """
    Returns list of dicts:
    {
        scheme_code: str,
        nav: float,
        date: YYYY-MM-DD
    }
    """

    records = []

    for line in raw_lines:
        line = line.strip()

        if (
            not line
            or line.startswith("Scheme Code")
            or "Schemes(" in line
            or "Mutual Fund" in line
        ):
            continue

        parts = [p.strip() for p in line.split(";")]
        if len(parts) < 6:
            continue

        scheme_code = clean_scheme_code(parts[0])
        nav = parts[4]
        date_str = parts[5]

        if not scheme_code or not nav or not date_str:
            continue

        try:
            nav = float(nav)
            date = datetime.strptime(date_str, "%d-%b-%Y").date().isoformat()
        except ValueError:
            continue

        records.append({
            "scheme_code": scheme_code,
            "nav": nav,
            "date": date
        })

    return records
