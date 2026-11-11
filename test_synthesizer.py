import json
from types import SimpleNamespace

import pytest

from agents import synthesizer

PAYLOAD = {"final_translation": "F", "confidence_score": 91, "issues_fixed": ["a"], "summary": "s"}


def _client(text=None, exc=None, delay=0.0):
    import asyncio

    async def generate_content(**kwargs):
        if delay:
            await asyncio.sleep(delay)
        if exc:
            raise exc
        return SimpleNamespace(text=text)

    return SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content)))


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "t")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "d")
    monkeypatch.setenv("GEMINI_API_KEY", "g")


async def _run(monkeypatch, client):
    monkeypatch.setattr(synthesizer, "get_gemini_client", lambda: client)
    return await synthesizer.call_synthesizer("o", "DRAFT", "a", "g", "c")


async def test_valid_json(monkeypatch):
    r = await _run(monkeypatch, _client(json.dumps(PAYLOAD)))
    assert r.final_translation == "F" and r.confidence_score == 91


async def test_code_fenced_json(monkeypatch):
    r = await _run(monkeypatch, _client("```json\n" + json.dumps(PAYLOAD) + "\n```"))
    assert r.final_translation == "F"


@pytest.mark.parametrize("client", [
    _client(None),
    _client("not json"),
    _client(json.dumps({**PAYLOAD, "confidence_score": 500})),
    _client(exc=RuntimeError("boom")),
])
async def test_failures_fall_back_to_draft(monkeypatch, client):
    r = await _run(monkeypatch, client)
    assert r.final_translation == "DRAFT"
    assert r.confidence_score == 75


async def test_timeout_falls_back(monkeypatch):
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "0.05")
    r = await _run(monkeypatch, _client(json.dumps(PAYLOAD), delay=1))
    assert r.final_translation == "DRAFT"
