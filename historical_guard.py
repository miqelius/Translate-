"""DeepSeek historical terminology reviewer."""
from agents.clients import deepseek_chat
from prompts.historical.v1 import GUARD_SYSTEM


async def call_guard(original: str, draft: str) -> str:
    return await deepseek_chat(
        GUARD_SYSTEM,
        f"ორიგინალი კონტექსტი:\n{original}\n\nთარგმანის დრაფტი:\n{draft}",
    )
