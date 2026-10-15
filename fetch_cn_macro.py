# fetch_cn_macro.py
import requests
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from config import get_required_env


# ===== 配置 =====
FRED_API_KEY = get_required_env("FRED_API_KEY")
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


def fred_latest_safe(series_id: str) -> Dict[str, Optional[Any]]:
    """
    Safe FRED fetch:
    - 永不抛异常
    - series 不存在 / API 报错 → 返回占位
    """
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }

    try:
        r = requests.get(FRED_URL, params=params, timeout=15)
        if r.status_code != 200:
            return {"date": None, "value": None}

        js = r.json()
        obs = js.get("observations", [])
        if not obs:
            return {"date": None, "value": None}

        o0 = obs[0]
        d = o0.get("date")
        v = o0.get("value")

        if v is None or v == ".":
            return {"date": d, "value": None}

        try:
            return {"date": d, "value": float(v)}
        except Exception:
            return {"date": d, "value": None}

    except Exception:
        # 网络 / JSON / 任何异常
        return {"date": None, "value": None}


def main() -> None:
    asof = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # =========================
    # CN 宏观 proxy（FRED）
    # =========================
    SERIES = {
        "cpi_yoy": "CPALTT01CNM659N",          # CPI YoY
        "usdcny": "DEXCHUS",                  # USD/CNY
        "industrial_production": "CHNPROINDMISMEI",
        "private_credit_gdp": "QCNPAF770A",
        # 未来可加，不影响现有结构
        # "unemployment": "LRUNTTTTCNM156S",
    }

    out: Dict[str, Any] = {
        "asof": asof,
        "inflation": {
            "cpi_yoy": {
                "fred_id": SERIES["cpi_yoy"],
                **fred_latest_safe(SERIES["cpi_yoy"]),
            }
        },
        "fx": {
            "usdcny": {
                "fred_id": SERIES["usdcny"],
                **fred_latest_safe(SERIES["usdcny"]),
            }
        },
        "activity": {
            "industrial_production": {
                "fred_id": SERIES["industrial_production"],
                **fred_latest_safe(SERIES["industrial_production"]),
            }
        },
        "credit": {
            "private_credit_gdp": {
                "fred_id": SERIES["private_credit_gdp"],
                **fred_latest_safe(SERIES["private_credit_gdp"]),
            }
        },
        "rates": {},  # 占位，未来扩展
    }

    print(out)


if __name__ == "__main__":
    main()
