import pytest

from engine import orchestrator
from engine.result import TranslationResult


@pytest.mark.asyncio
async def test_orchestrator_calls_pipeline_in_order(monkeypatch):
    calls = []

    async def translator(text):
        calls.append(("translator", text))
        return "draft"

    async def reviewer(name, original, draft):
        calls.append((name, original, draft))
        return name + "-notes"

    async def synthesizer(original, draft, accuracy, guard, style):
        calls.append(("synthesizer", original, draft, accuracy, guard, style))
        return TranslationResult(
            final_translation="final", confidence_score=88, summary="ok"
        )

    monkeypatch.setattr(orchestrator, "call_translator", translator)
    monkeypatch.setattr(
        orchestrator, "call_accuracy_reviewer",
        lambda original, draft: reviewer("accuracy", original, draft),
    )
    monkeypatch.setattr(
        orchestrator, "call_guard",
        lambda original, draft: reviewer("guard", original, draft),
    )
    monkeypatch.setattr(
        orchestrator, "call_critic",
        lambda original, draft: reviewer("style", original, draft),
    )
    monkeypatch.setattr(orchestrator, "call_synthesizer", synthesizer)

    result = await orchestrator.translate_historical("source text")
    assert result.final_translation == "final"
    assert calls[0] == ("translator", "source text")
    assert calls[-1] == (
        "synthesizer", "source text", "draft",
        "accuracy-notes", "guard-notes", "style-notes",
    )


@pytest.mark.asyncio
async def test_orchestrator_reports_stages_and_survives_callback_errors(monkeypatch):
    async def ok(*args):
        return "x"

    async def synth(*args):
        return TranslationResult(final_translation="f", confidence_score=1, summary="s")

    for name in ("call_translator", "call_accuracy_reviewer", "call_guard", "call_critic"):
        monkeypatch.setattr(orchestrator, name, ok)
    monkeypatch.setattr(orchestrator, "call_synthesizer", synth)

    seen = []

    async def on_stage(stage):
        seen.append(stage)
        raise RuntimeError("telegram down")

    result = await orchestrator.translate_historical("t", on_stage=on_stage)
    assert result.final_translation == "f"
    assert seen == [orchestrator.Stage.TRANSLATE, orchestrator.Stage.REVIEW,
                    orchestrator.Stage.SYNTHESIZE]
