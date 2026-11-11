"""DeepSeek translation agent."""
from agents.clients import deepseek_chat
from prompts.historical.v1 import TRANSLATOR_SYSTEM


async def call_translator(text: str) -> str:
    # An empty draft would poison every later stage, so fail fast.
    return await deepseek_chat(TRANSLATOR_SYSTEM, text, require_text=True)
