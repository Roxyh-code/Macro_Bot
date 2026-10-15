import os
import requests
from datetime import datetime

from config import DISCORD_LOG_PATH, get_required_env

LOG = DISCORD_LOG_PATH

def dlog(msg: str) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

DISCORD_BOT_TOKEN = get_required_env("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = get_required_env("DISCORD_CHANNEL_ID")

def send_message(channel_id: str, token: str, content: str) -> None:
    channel_id = str(channel_id).strip()
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }

    payload = {"content": content}

    dlog(f"POST {url}")
    dlog(f"content_len={len(content)} content_head={content[:200]!r}")

    r = requests.post(url, headers=headers, json=payload, timeout=30)

    dlog(f"status={r.status_code} resp_head={r.text[:300]!r}")

    # 让失败直接冒出来
    r.raise_for_status()

def main() -> None:
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        raise SystemExit("Missing env vars: DISCORD_BOT_TOKEN and/or DISCORD_CHANNEL_ID")

    # 先发一条测试
    send_message(DISCORD_CHANNEL_ID, DISCORD_BOT_TOKEN, "✅ nanobot macro brief test: hello!")

if __name__ == "__main__":
    main()
