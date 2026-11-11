"""Gemini synthesis agent, retaining the original fallback behavior."""
import asyncio
import json
import logging

from google.genai import types as gemini_types

from agents.clients import GEMINI_MODEL, get_gemini_client
from core.config import get_settings
from engine.result import TranslationResult
from prompts.historical.v1 import synthesis_prompt

logger = logging.getLogger(__name__)


def _strip_code_fence(text: str) -> str:
    """Gemini occasionally wraps JSON in ```json fences despite the JSON mime type."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text.strip()


async def call_synthesizer(original: str, draft: str, accuracy_notes: str,
                           guard_notes: str, critic_notes: str) -> TranslationResult:
    prompt = synthesis_prompt(original, draft, accuracy_notes, guard_notes, critic_notes)
    try:
        timeout = get_settings().request_timeout_seconds
        response = await asyncio.wait_for(
            get_gemini_client().aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=gemini_types.GenerateContentConfig(response_mime_type="application/json"),
            ),
            timeout=timeout,
        )
        if not response.text:
            raise ValueError("Gemini returned an empty response")
        return TranslationResult(**json.loads(_strip_code_fence(response.text)))
    except Exception:
        logger.exception("Gemini Synthesizer error; returning original draft fallback")
        return TranslationResult(
            final_translation=draft,
            confidence_score=75,
            issues_fixed=["სინთეზის შეცდომა — გამოყენებულია DeepSeek-ის საწყისი დრაფტი."],
            summary="Gemini-მ ვერ მოახერხა სრულყოფილი სინთეზი.",
        )
