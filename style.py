"""DeepSeek style reviewer."""
from agents.clients import deepseek_chat
from prompts.historical.v1 import CRITIC_SYSTEM


async def call_critic(original: str, draft: str) -> str:
    return await deepseek_chat(
        CRITIC_SYSTEM,
        f"ორიგინალი:\n{original}\n\nთარგმანის დრაფტი:\n{draft}",
    )
