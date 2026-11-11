"""Environment configuration. Existing variable names are intentionally preserved."""
import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

_REQUIRED = ("BOT_TOKEN", "DEEPSEEK_API_KEY", "GEMINI_API_KEY")


@dataclass(frozen=True)
class Settings:
    bot_token: str
    deepseek_api_key: str
    gemini_api_key: str
    # Optional production controls (all have safe defaults).
    allowed_user_ids: frozenset[int] = frozenset()  # empty = bot is open to everyone
    max_concurrent_jobs: int = 5  # global cap on simultaneous pipelines (cost/rate control)
    request_timeout_seconds: float = 90.0  # per provider call
    log_level: str = "INFO"


def _get(env: Mapping[str, str], name: str) -> str:
    return (env.get(name) or "").strip()


def _parse_user_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.add(int(part))
        except ValueError as exc:
            raise ValueError(f"ALLOWED_USER_IDS contains a non-numeric id: {part!r}") from exc
    return frozenset(ids)


def _parse_positive(env: Mapping[str, str], name: str, default: float, cast: type) -> float:
    raw = _get(env, name)
    if not raw:
        return default
    try:
        value = cast(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0, got {raw!r}")
    return value


def get_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    values = {name: _get(env, name) for name in _REQUIRED}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))
    return Settings(
        bot_token=values["BOT_TOKEN"],
        deepseek_api_key=values["DEEPSEEK_API_KEY"],
        gemini_api_key=values["GEMINI_API_KEY"],
        allowed_user_ids=_parse_user_ids(_get(env, "ALLOWED_USER_IDS")),
        max_concurrent_jobs=int(_parse_positive(env, "MAX_CONCURRENT_JOBS", 5, int)),
        request_timeout_seconds=_parse_positive(env, "REQUEST_TIMEOUT_SECONDS", 90.0, float),
        log_level=(_get(env, "LOG_LEVEL") or "INFO").upper(),
    )
