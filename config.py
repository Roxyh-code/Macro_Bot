import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
TRACE_PATH = ROOT_DIR / "RUN_TRACE.log"
DISCORD_LOG_PATH = ROOT_DIR / "discord_api.log"


def _load_local_dotenv() -> None:
    dotenv_path = ROOT_DIR / ".env"
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_local_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


def get_optional_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()
