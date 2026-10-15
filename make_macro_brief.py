import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent


# ---------- utils ----------
def _get(path: str, obj: Dict[str, Any]) -> Optional[Any]:
    """Safe dict getter by dotted path, e.g. 'series.us_10y.value'."""
    cur: Any = obj
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _fnum(x: Any, nd: int = 2) -> str:
    if x is None:
        return "NA"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return "NA"


def _run_and_literal_eval(py_file: str) -> Dict[str, Any]:
    """
    Runs a script that prints a Python dict, then parses it via ast.literal_eval.
    - text=False + decode utf-8 with replace: avoids gbk/emoji issues under Task Scheduler.
    """
    import ast

    script_path = (ROOT_DIR / py_file).resolve()
    p = subprocess.run(
        ["python", str(script_path)],
        capture_output=True,
        text=False,
        check=False,
        cwd=str(ROOT_DIR),
    )

    out = (p.stdout or b"").decode("utf-8", errors="replace").strip()
    err = (p.stderr or b"").decode("utf-8", errors="replace").strip()

    if p.returncode != 0:
        raise RuntimeError(
            f"{py_file} failed (returncode={p.returncode}).\n"
            f"----- STDOUT -----\n{out}\n\n"
            f"----- STDERR -----\n{err}\n"
        )

    if not out:
        raise ValueError(f"{py_file} printed empty stdout (expected a dict). stderr:\n{err}")

    data = ast.literal_eval(out)
    if not isinstance(data, dict):
        raise ValueError(f"{py_file} did not return a dict-like output. got={type(data)}")
    return data


def load_us_macro() -> Dict[str, Any]:
    return _run_and_literal_eval("fetch_us_macro.py")


def load_cn_macro() -> Dict[str, Any]:
    return _run_and_literal_eval("fetch_cn_macro.py")


def _row(label: str, us_text: str, cn_text: str) -> str:
    return f"- **{label}** | US: **{us_text}** | CN: **{cn_text}**"


def build_brief(us: Dict[str, Any], cn: Dict[str, Any]) -> str:
    # ---------- US fields (from your fetch_us_macro.py) ----------
    asof_us = _get("asof", us) or ""
    us_10y = _get("series.us_10y.value", us)
    us_10y_d = _get("series.us_10y.date", us) or ""
    us_2y = _get("series.us_2y.value", us)
    us_real10 = _get("series.us_10y_real.value", us)
    us_hy = _get("series.us_hy_oas.value", us)
    us_vix = _get("series.vix.value", us)

    # Spread is optional (your fetch may or may not compute it)
    us_spread = _get("series.us_term_spread_10y2y.value", us)
    if us_spread is None and us_10y is not None and us_2y is not None:
        try:
            us_spread = float(us_10y) - float(us_2y)
        except Exception:
            us_spread = None

    # ---------- CN fields (from our fetch_cn_macro.py) ----------
    asof_cn = _get("asof", cn) or ""
    cn_cpi = _get("inflation.cpi_yoy.value", cn)
    cn_cpi_d = _get("inflation.cpi_yoy.date", cn) or ""
    cn_fx = _get("fx.usdcny.value", cn)
    cn_fx_d = _get("fx.usdcny.date", cn) or ""
    cn_ip = _get("activity.industrial_production.value", cn)
    cn_ip_d = _get("activity.industrial_production.date", cn) or ""
    cn_credit_gdp = _get("credit.private_credit_gdp.value", cn)
    cn_credit_gdp_d = _get("credit.private_credit_gdp.date", cn) or ""

    # rates placeholder (if later you add rates.interbank_3m in fetch_cn_macro.py)
    cn_3m = _get("rates.interbank_3m.value", cn)
    cn_3m_d = _get("rates.interbank_3m.date", cn) or ""

    # pick a common asof
    asof = asof_us or asof_cn

    # ---------- pretty text ----------
    us10_txt = f"{_fnum(us_10y, 2)}%（{us_10y_d}）" if us_10y is not None else "NA"
    us2_txt = f"{_fnum(us_2y, 2)}%" if us_2y is not None else "NA"
    spread_txt = f"{_fnum(us_spread, 2)} pct" if us_spread is not None else "NA"
    real10_txt = f"{_fnum(us_real10, 2)}%" if us_real10 is not None else "NA"
    hy_txt = f"{_fnum(us_hy, 2)}%" if us_hy is not None else "NA"
    vix_txt = f"{_fnum(us_vix, 1)}" if us_vix is not None else "NA"

    cpi_txt = f"{_fnum(cn_cpi, 2)}%（{cn_cpi_d}）" if cn_cpi is not None else "NA"
    fx_txt = f"{_fnum(cn_fx, 4)}（{cn_fx_d}）" if cn_fx is not None else "NA"
    ip_txt = f"{_fnum(cn_ip, 2)}（{cn_ip_d}）" if cn_ip is not None else "NA"
    cr_txt = f"{_fnum(cn_credit_gdp, 1)}%（{cn_credit_gdp_d}）" if cn_credit_gdp is not None else "NA"
    cn3m_txt = f"{_fnum(cn_3m, 2)}%（{cn_3m_d}）" if cn_3m is not None else "NA"

    # ---------- rough signals (v1) ----------
    risk_flags = []

    # US risk appetite heuristics
    try:
        if us_hy is not None and float(us_hy) < 3.0:
            risk_flags.append("US: HY利差偏紧（risk-on）")
    except Exception:
        pass
    try:
        if us_vix is not None and float(us_vix) < 14:
            risk_flags.append("US: VIX偏低（情绪偏乐观）")
    except Exception:
        pass
    try:
        if us_spread is not None and float(us_spread) < 0:
            risk_flags.append("US: 期限仍倒挂（增长/政策预期博弈）")
    except Exception:
        pass

    # CN simple heuristics (very rough)
    try:
        if cn_cpi is not None and float(cn_cpi) <= 0.5:
            risk_flags.append("CN: 通胀偏弱（更像宽松/托底框架）")
    except Exception:
        pass
    try:
        if cn_fx is not None and float(cn_fx) >= 7.30:
            risk_flags.append("CN: 汇率压力偏大（外部约束）")
    except Exception:
        pass

    # ---------- output ----------
    lines = []
    lines.append(f"📌 **宏观简报（US vs CN）**  | asof: {asof}")
    lines.append("")

    lines.append("**利率 / 利差（对齐）**")
    lines.append(_row("10Y 国债收益率", us10_txt, "NA"))
    lines.append(_row("2Y 国债收益率", us2_txt, "NA"))
    lines.append(_row("10Y-2Y 期限利差", spread_txt, "NA"))
    lines.append(_row("10Y 实际利率", real10_txt, "NA"))
    lines.append(_row("CN 3M 同业利率（占位）", "NA", cn3m_txt))
    lines.append("")

    lines.append("**通胀 / 活动（对齐）**")
    lines.append(_row("CPI YoY", "NA", cpi_txt))
    lines.append(_row("工业生产指数", "NA", ip_txt))
    lines.append("")

    lines.append("**信用 / 风险（对齐）**")
    lines.append(_row("HY OAS", hy_txt, "NA"))
    lines.append(_row("VIX", vix_txt, "NA"))
    lines.append(_row("USD/CNY", "NA", fx_txt))
    lines.append(_row("Private Credit/GDP", "NA", cr_txt))
    lines.append("")

    if risk_flags:
        lines.append("**风险提示（粗）**")
        for r in risk_flags:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("**阶段判断（粗）**")
    # very simple combined line, you will upgrade later
    if us_spread is not None:
        try:
            if float(us_spread) > 0 and (us_hy is not None and float(us_hy) < 4.0):
                lines.append("- US：利差修复 + 信用压力不大（偏“风险可控/偏顺风”）")
            elif float(us_spread) < 0:
                lines.append("- US：期限倒挂仍在（偏“增长/政策博弈”）")
            else:
                lines.append("- US：中性（等待利率与信用给方向）")
        except Exception:
            lines.append("- US：中性（等待利率与信用给方向）")
    else:
        lines.append("- US：中性（等待利率与信用给方向）")

    # CN placeholder conclusion
    if cn_cpi is not None:
        try:
            if float(cn_cpi) <= 0.5:
                lines.append("- CN：通胀偏弱（更可能是“托底/宽松预期”主导）")
            else:
                lines.append("- CN：中性（等待社融/M1-M2/就业等更关键变量）")
        except Exception:
            lines.append("- CN：中性（等待社融/M1-M2/就业等更关键变量）")
    else:
        lines.append("- CN：中性（等待社融/M1-M2/就业等更关键变量）")

    return "\n".join(lines)


def main() -> None:
    us = load_us_macro()
    cn = load_cn_macro()
    brief = build_brief(us, cn)
    print(brief)


if __name__ == "__main__":
    main()
