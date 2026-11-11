from unittest.mock import AsyncMock, MagicMock

from aiogram.exceptions import TelegramBadRequest

from apps.telegram.formatters import TELEGRAM_MSG_LIMIT, safe_edit, send_result
from engine.result import TranslationResult


def _msgs():
    status, message = MagicMock(), MagicMock()
    status.edit_text = AsyncMock()
    message.answer_document = AsyncMock()
    return message, status


def _bad_request():
    return TelegramBadRequest(method=MagicMock(), message="bad")


async def test_short_result_edits_status_with_escaped_html():
    message, status = _msgs()
    await send_result(message, status, TranslationResult(
        final_translation="<b>x</b>", confidence_score=90, issues_fixed=[], summary="s&t"))
    text = status.edit_text.await_args.args[0]
    assert "&lt;b&gt;x&lt;/b&gt;" in text and "s&amp;t" in text
    assert "ხარვეზები არ დაფიქსირებულა" in text
    message.answer_document.assert_not_awaited()


async def test_long_result_goes_to_txt_file():
    message, status = _msgs()
    long_text = "ა" * (TELEGRAM_MSG_LIMIT + 10)
    await send_result(message, status, TranslationResult(
        final_translation=long_text, confidence_score=80, summary="s"))
    doc = message.answer_document.await_args.args[0]
    assert doc.filename == "historical_translation.txt"
    assert doc.data.decode("utf-8") == long_text


async def test_telegram_rejection_falls_back_to_file():
    message, status = _msgs()
    status.edit_text.side_effect = [_bad_request(), None]
    await send_result(message, status, TranslationResult(
        final_translation="short", confidence_score=80, summary="s"))
    message.answer_document.assert_awaited_once()


async def test_safe_edit_swallows_telegram_errors():
    _, status = _msgs()
    status.edit_text.side_effect = _bad_request()
    assert await safe_edit(status, "x") is False
