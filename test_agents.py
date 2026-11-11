from types import SimpleNamespace

import pytest

from agents import accuracy, clients, historical_guard, style, translator


def _fake_client(content, seen):
    async def create(**kwargs):
        seen.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))


async def test_translator_sends_system_prompt_and_text(monkeypatch):
    seen = []
    monkeypatch.setattr(clients, "get_deepseek_client", lambda: _fake_client("draft", seen))
    assert await translator.call_translator("hello") == "draft"
    assert seen[0]["model"] == "deepseek-chat"
    assert seen[0]["messages"][1] == {"role": "user", "content": "hello"}


@pytest.mark.parametrize("content", ["", "   ", None])
async def test_translator_rejects_empty_output(monkeypatch, content):
    monkeypatch.setattr(clients, "get_deepseek_client", lambda: _fake_client(content, []))
    with pytest.raises(ValueError):
        await translator.call_translator("hello")


@pytest.mark.parametrize("fn,label", [
    (accuracy.call_accuracy_reviewer, "ორიგინალი:\nO"),
    (historical_guard.call_guard, "ორიგინალი კონტექსტი:\nO"),
    (style.call_critic, "ორიგინალი:\nO"),
])
async def test_reviewers_message_shape(monkeypatch, fn, label):
    seen = []
    monkeypatch.setattr(clients, "get_deepseek_client", lambda: _fake_client("notes", seen))
    assert await fn("O", "D") == "notes"
    assert seen[0]["messages"][1]["content"] == f"{label}\n\nთარგმანის დრაფტი:\nD"


def test_clients_are_lazy_and_cached(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "t")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "d")
    monkeypatch.setenv("GEMINI_API_KEY", "g")
    c = clients.get_deepseek_client()
    assert c is clients.get_deepseek_client()
    assert c.max_retries == clients.PROVIDER_MAX_RETRIES
    assert c.timeout == 90.0
    assert clients.get_gemini_client() is clients.get_gemini_client()
