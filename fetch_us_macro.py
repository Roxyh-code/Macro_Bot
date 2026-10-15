import os
import requests
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

from config import get_required_env

# ===== 配置 =====
FRED_API_KEY = get_required_env("FRED_API_KEY")

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES: Dict[str, str] = {
    "DGS10": "us_10y",
    "DGS2": "us_2y",
    "DFII10": "us_10y_real",
    "BAMLH0A0HYM2": "us_hy_oas",
    "VIXCLS": "vix",
}

# ===== 函数 =====
def get_latest(series_id: str, api_key: str) -> Tuple[Optional[str], Optional[float]]:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 10,
    }
    r = requests.get(FRED_URL, params=params, timeout=20)
    r.raise_for_status()

    for row in r.json().get("observations", []):
        v = row.get("value")
        if v is None or v == ".":
            continue
        try:
            return row["date"], float(v)
        except ValueError:
            continue

    return None, None


def main() -> None:
    out: Dict[str, Dict[str, object]] = {
        "asof": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "series": {}
    }

    for sid, name in SERIES.items():
        d, v = get_latest(sid, FRED_API_KEY)
        out["series"][name] = {
            "fred_id": sid,
            "date": d,
            "value": v
        }

    # ===== 派生：期限利差 =====
    v10 = out["series"]["us_10y"]["value"]
    v2 = out["series"]["us_2y"]["value"]

    if isinstance(v10, float) and isinstance(v2, float):
        out["series"]["us_term_spread_10y2y"] = {
            "value": round(v10 - v2, 4),
            "units": "pct_points"
        }

    print(out)


if __name__ == "__main__":
    main()
