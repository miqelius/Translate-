"""Lazy provider-client factories; importing modules does not require API secrets."""
from functools import lru_cache
from typing import Any

from google import genai
from openai import AsyncOpenAI

from core.config import get_settings

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
GEMINI_MODEL = "gemini-2.5-flash"
PROVIDER_MAX_RETRIES = 2  # SDK-level retries for 429/5xx/connection errors


@lru_cache(maxsize=1)
def get_deepseek_client() -> AsyncOpenAI:
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=DEEPSEEK_BASE_URL,
        timeout=settings.request_timeout_seconds,
        max_retries=PROVIDER_MAX_RETRIES,
    )


@lru_cache(maxsize=1)
def get_gemini_client() -> Any:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


async def deepseek_chat(system: str, user: str, *, require_text: bool = False) -> str:
    """One DeepSeek chat completion. Empty output is an error when `require_text` is set."""
    response = await get_deepseek_client().chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response.choices[0].message.content or ""
    if require_text and not content.strip():
        raise ValueError("DeepSeek returned an empty response")
    return content
