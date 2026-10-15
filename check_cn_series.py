import requests

from config import get_required_env

FRED_API_KEY = get_required_env("FRED_API_KEY")
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


# ========= CN 候选指标全集 =========
SERIES = {
    # ---------- 通胀 ----------
    "CPI YoY (FRED old)": "CPALTT01CNM659N",
    "CPI All Items (OECD MEI)": "CHNCPIALLMINMEI",

    # ---------- 工业 / 产出 ----------
    "Industrial Production (OECD MEI)": "CHNPROINDMISMEI",
    "Manufacturing Production (OECD)": "CHNMANPRODMINMEI",

    # ---------- 汇率 ----------
    "USD/CNY (DEXCHUS)": "DEXCHUS",

    # ---------- 信用 / 杠杆（BIS / FRED proxy） ----------
    "Private Credit to GDP (BIS)": "QCNPAF770A",
    "Total Credit to Non-Financial (BIS)": "QCNPAF750A",

    # ---------- 货币 / 金融条件（如果有就赚到） ----------
    "M2 Money Stock (proxy)": "MYAGM2CNM189S",  # 这条经常不可用，但值得测
}


def get_latest(series_id: str):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 12,
    }

    try:
        r = requests.get(FRED_URL, params=params, timeout=15)
        status = r.status_code
        if status != 200:
            return status, None, None

        obs = r.json().get("observations", [])
        for row in obs:
            v = row.get("value")
            if v is None or v == ".":
                continue
            try:
                return status, row.get("date"), float(v)
            except Exception:
                continue

        return status, None, None

    except Exception as e:
        return "ERR", None, None


if __name__ == "__main__":
    print("=== CN SERIES CHECK (FRED / OECD / BIS proxies) ===\n")
    for label, sid in SERIES.items():
        status, d, v = get_latest(sid)
        print(
            f"{label:<38} | {sid:<18} | "
            f"status={status:<4} | date={str(d):<10} | value={v}"
        )
