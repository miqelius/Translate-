"""DeepSeek accuracy reviewer."""
from agents.clients import deepseek_chat
from prompts.historical.v1 import ACCURACY_SYSTEM


async def call_accuracy_reviewer(original: str, draft: str) -> str:
    return await deepseek_chat(
        ACCURACY_SYSTEM,
        f"ორიგინალი:\n{original}\n\nთარგმანის დრაფტი:\n{draft}",
    )
