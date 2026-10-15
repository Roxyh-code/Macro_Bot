import requests

from config import get_required_env

FRED_API_KEY = get_required_env("FRED_API_KEY")

url = "https://api.stlouisfed.org/fred/series/observations"
params = {
    "series_id": "DGS10",          # 10Y Treasury
    "api_key": FRED_API_KEY,
    "file_type": "json",
    "sort_order": "desc",
    "limit": 1
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()["observations"][0]

print("Date:", data["date"])
print("10Y Treasury Yield:", data["value"])
