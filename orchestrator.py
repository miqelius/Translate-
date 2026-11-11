"""Historical pipeline orchestration. Pipeline order matches the original bot."""
import asyncio
from collections.abc import Awaitable, Callable
from enum import Enum

from agents.accuracy import call_accuracy_reviewer
from agents.historical_guard import call_guard
from agents.style import call_critic
from agents.synthesizer import call_synthesizer
from agents.translator import call_translator
from engine.result import TranslationResult


class Stage(str, Enum):
    TRANSLATE = "translate"
    REVIEW = "review"
    SYNTHESIZE = "synthesize"


StageCallback = Callable[[Stage], Awaitable[None]]


async def _notify(on_stage: StageCallback | None, stage: Stage) -> None:
    """Progress reporting must never break the pipeline."""
    if on_stage is None:
        return
    try:
        await on_stage(stage)
    except Exception:  # noqa: BLE001 - UI failures are non-fatal
        pass


async def translate_historical(
    text: str, on_stage: StageCallback | None = None
) -> TranslationResult:
    await _notify(on_stage, Stage.TRANSLATE)
    draft = await call_translator(text)

    await _notify(on_stage, Stage.REVIEW)
    accuracy_feedback, guard_feedback, critic_feedback = await asyncio.gather(
        call_accuracy_reviewer(text, draft),
        call_guard(text, draft),
        call_critic(text, draft),
    )

    await _notify(on_stage, Stage.SYNTHESIZE)
    return await call_synthesizer(
        text, draft, accuracy_feedback, guard_feedback, critic_feedback
    )
