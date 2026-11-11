import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APITimeoutError, AuthenticationError, RateLimitError

from apps.telegram import handlers
from core.config import Settings
from engine.orchestrator import Stage
from engine.result import TranslationResult

SETTINGS = Settings("t", "d", "g")
RESULT = TranslationResult(final_translation="ok", confidence_score=90, summary="s")


def _message(text="hello", user_id=1):
    status = MagicMock()
    status.edit_text = AsyncMock()
    m = MagicMock()
    m.text = text
    m.from_user = SimpleNamespace(id=user_id)
    m.chat = SimpleNamespace(id=10)
    m.reply = AsyncMock(return_value=status)
    m.answer = AsyncMock()
    m.status = status
    return m


def _bot():
    return SimpleNamespace(send_chat_action=AsyncMock())


def _slots(n=5):
    return asyncio.Semaphore(n)


def _api_error(cls):
    """Build an SDK exception without depending on the SDK's HTTP-library constructor."""
    return cls.__new__(cls)


async def _handle(m, settings=SETTINGS, slots=None):
    await handlers.process_translation_request(m, _bot(), settings, slots or _slots())


async def test_happy_path_reports_progress_and_sends_result(monkeypatch):
    async def fake(text, on_stage=None):
        for s in Stage:
            await on_stage(s)
        return RESULT

    monkeypatch.setattr(handlers, "translate_historical", fake)
    m = _message()
    await _handle(m)
    stages = [c.args[0] for c in m.status.edit_text.await_args_list]
    assert any("1/3" in s for s in stages) and any("3/3" in s for s in stages)
    assert "ok" in stages[-1]
    assert handlers.active_users == set()


async def test_too_long_rejected_before_any_api_call(monkeypatch):
    called = AsyncMock()
    monkeypatch.setattr(handlers, "translate_historical", called)
    m = _message("word " * 501)
    await _handle(m)
    assert m.reply.await_args.args[0] == handlers.TOO_LONG_TEXT
    called.assert_not_awaited()


async def test_exactly_500_words_accepted(monkeypatch):
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock(return_value=RESULT))
    await _handle(_message("word " * 500))
    handlers.translate_historical.assert_awaited_once()


async def test_busy_user_gets_wait_message(monkeypatch):
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock())
    handlers.active_users.add(1)
    m = _message()
    await _handle(m)
    assert m.reply.await_args.args[0] == handlers.BUSY_TEXT
    handlers.translate_historical.assert_not_awaited()


async def test_allowlist_blocks_strangers(monkeypatch):
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock())
    s = Settings("t", "d", "g", allowed_user_ids=frozenset({99}))
    m = _message(user_id=1)
    await _handle(m, s)
    assert m.reply.await_args.args[0] == handlers.DENIED_TEXT
    handlers.translate_historical.assert_not_awaited()
    ok = _message(user_id=99)
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock(return_value=RESULT))
    await _handle(ok, s)
    handlers.translate_historical.assert_awaited_once()


@pytest.mark.parametrize("exc,expected", [
    (_api_error(AuthenticationError), "API გასაღები"),
    (_api_error(RateLimitError), "გადატვირთულია"),
    (_api_error(APITimeoutError), "მიუწვდომელია"),
    (RuntimeError("x"), "სისტემური შეცდომა"),
])
async def test_errors_map_to_user_messages_and_release_user(monkeypatch, exc, expected):
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock(side_effect=exc))
    m = _message()
    await _handle(m)
    assert expected in m.status.edit_text.await_args.args[0]
    assert handlers.active_users == set()


async def test_error_falls_back_to_reply_when_status_edit_fails(monkeypatch):
    monkeypatch.setattr(handlers, "translate_historical", AsyncMock(side_effect=RuntimeError("x")))
    m = _message()
    from aiogram.exceptions import TelegramBadRequest
    m.status.edit_text.side_effect = TelegramBadRequest(method=MagicMock(), message="gone")
    await _handle(m)
    assert "სისტემური შეცდომა" in m.reply.await_args_list[-1].args[0]


async def test_global_concurrency_cap_serializes_jobs(monkeypatch):
    running = peak = 0

    async def fake(text, on_stage=None):
        nonlocal running, peak
        running += 1
        peak = max(peak, running)
        await asyncio.sleep(0.02)
        running -= 1
        return RESULT

    monkeypatch.setattr(handlers, "translate_historical", fake)
    slots = _slots(1)
    await asyncio.gather(*[_handle(_message(user_id=i), slots=slots) for i in range(1, 4)])
    assert peak == 1


async def test_start_command_uses_html_and_respects_allowlist():
    m = _message()
    await handlers.cmd_start(m, SETTINGS)
    assert "<b>DeepSeek</b>" in m.answer.await_args.args[0]
    assert "**" not in handlers.START_TEXT
    denied = _message(user_id=1)
    await handlers.cmd_start(denied, Settings("t", "d", "g", allowed_user_ids=frozenset({2})))
    assert denied.answer.await_args.args[0] == handlers.DENIED_TEXT


def test_register_handlers_wires_settings_and_router():
    from aiogram import Dispatcher
    dp = Dispatcher()
    handlers.register_handlers(dp, SETTINGS)
    assert dp.workflow_data["settings"] is SETTINGS
    assert isinstance(dp.workflow_data["job_slots"], asyncio.Semaphore)
