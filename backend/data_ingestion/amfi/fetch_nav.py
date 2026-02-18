import requests
import time

AMFI_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"

def fetch_amfi_nav(retries=3, timeout=30):
    """
    Fetches AMFI NAVAll.txt with retry & timeout protection.
    Returns list of lines (same as original behavior).
    """

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt {attempt}: Fetching AMFI NAV data...")
            response = requests.get(AMFI_URL, timeout=timeout)
            response.raise_for_status()

            return response.text.splitlines()

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            last_error = e
            time.sleep(5)

    raise RuntimeError("AMFI NAV fetch failed after multiple retries") from last_error

