import os
import subprocess
import requests
from datetime import datetime

from config import ROOT_DIR, TRACE_PATH, get_required_env

TRACE = TRACE_PATH

DISCORD_BOT_TOKEN = get_required_env("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = get_required_env("DISCORD_CHANNEL_ID")

def trace(msg: str) -> None:
    with open(TRACE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def safe_decode(b: bytes) -> str:
    if b is None:
        return ""
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("utf-8", errors="replace")

def split_discord_messages(text: str, limit: int = 1900) -> list[str]:
    """Discord 单条 2000 字上限，留点余量。优先按换行切，切不开再硬切。"""
    text = (text or "").strip()
    if not text:
        return ["(empty brief)"]

    parts: list[str] = []
    buf = ""
    for line in text.splitlines(True):  # keepends
        if len(buf) + len(line) <= limit:
            buf += line
        else:
            if buf.strip():
                parts.append(buf.strip())
            buf = line

            # 单行都超长：硬切
            while len(buf) > limit:
                parts.append(buf[:limit])
                buf = buf[limit:]

    if buf.strip():
        parts.append(buf.strip())
    return parts

def discord_post(channel_id: str, token: str, content: str) -> None:
    url = f"https://discord.com/api/v10/channels/{str(channel_id).strip()}/messages"
    headers = {"Authorization": f"Bot {token}"}
    payload = {"content": content}

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    trace(f"Discord POST status={r.status_code} resp_head={r.text[:200]!r}")
    if not (200 <= r.status_code < 300):
        raise RuntimeError(f"Discord API error {r.status_code}: {r.text}")

def build_brief_via_subprocess() -> str:
    trace("about to run make_macro_brief")
    p = subprocess.run(
        ["python", str(ROOT_DIR / "make_macro_brief.py")],
        capture_output=True,
        text=False,  # 关键：避免 GBK 解码坑
        cwd=str(ROOT_DIR),
    )
    out = safe_decode(p.stdout)
    err = safe_decode(p.stderr)

    trace(f"make_macro_brief returncode={p.returncode}")
    if err.strip():
        trace("make_macro_brief stderr:\n" + err[:2000])

    if p.returncode != 0:
        raise RuntimeError("make_macro_brief failed (see stderr in trace)")

    return out.strip()

def main() -> None:
    trace("run_and_send_brief START")
    trace(f"cwd={os.path.basename(str(ROOT_DIR))}")

    token = os.getenv("DISCORD_BOT_TOKEN", DISCORD_BOT_TOKEN).strip()
    channel_id = os.getenv("DISCORD_CHANNEL_ID", DISCORD_CHANNEL_ID).strip()

    if not token or token == "YOUR_BOT_TOKEN_HERE":
        raise RuntimeError("Discord bot token missing")
    if not channel_id or channel_id == "YOUR_CHANNEL_ID_HERE":
        raise RuntimeError("Discord channel id missing")

    brief = build_brief_via_subprocess()
    trace(f"brief_len={len(brief)} brief_head={brief[:80]!r}")

    parts = split_discord_messages(brief, limit=1900)
    trace(f"sending_parts={len(parts)}")

    for i, part in enumerate(parts, 1):
        trace(f"sending part {i}/{len(parts)} len={len(part)}")
        discord_post(channel_id, token, part)

    trace("DONE")

if __name__ == "__main__":
    main()

