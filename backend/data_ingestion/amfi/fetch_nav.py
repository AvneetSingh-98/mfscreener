import requests

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

def fetch_amfi_nav():
    response = requests.get(AMFI_URL)
    response.raise_for_status()
    return response.text.splitlines()
