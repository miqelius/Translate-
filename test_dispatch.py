"""End-to-end routing through a real aiogram Dispatcher with a stubbed Telegram transport."""
import datetime

from aiogram import Bot, Dispatcher
from aiogram.methods import SendMessage, TelegramMethod
from aiogram.types import Chat, Message, Update, User

from apps.telegram import handlers
from core.config import Settings
from engine.result import TranslationResult

NOW = datetime.datetime.now(datetime.timezone.utc)


def _update(text, chat_type="private", uid=5, update_id=1):
    chat = Chat(id=uid, type=chat_type)
    msg = Message(message_id=update_id, date=NOW, chat=chat,
                  from_user=User(id=uid, is_bot=False, first_name="t"), text=text,
                  entities=[{"type": "bot_command", "offset": 0, "length": len(text)}]
                  if text.startswith("/") else None)
    return Update(update_id=update_id, message=msg)


async def _setup(monkeypatch, translate):
    sent: list[TelegramMethod] = []

    async def fake_call(self, method, request_timeout=None):
        sent.append(method)
        if isinstance(method, SendMessage):
            return Message(message_id=99, date=NOW, chat=Chat(id=5, type="private"),
                           text=method.text).as_(self)
        return True

    monkeypatch.setattr(Bot, "__call__", fake_call)
    monkeypatch.setattr(handlers, "translate_historical", translate)
    dp = Dispatcher()
    handlers.register_handlers(dp, Settings("t", "d", "g"))
    return Bot("123456:TESTTOKEN"), dp, sent


async def test_plain_text_is_translated(monkeypatch):
    calls = []

    async def translate(text, on_stage=None):
        calls.append(text)
        return TranslationResult(final_translation="done", confidence_score=90, summary="s")

    bot, dp, sent = await _setup(monkeypatch, translate)
    await dp.feed_update(bot, _update("hello world"))
    assert calls == ["hello world"]
    assert any("done" in (getattr(m, "text", "") or "") for m in sent)


async def test_commands_and_group_chats_never_reach_the_pipeline(monkeypatch):
    calls = []

    async def translate(text, on_stage=None):
        calls.append(text)
        raise AssertionError("must not run")

    bot, dp, sent = await _setup(monkeypatch, translate)
    await dp.feed_update(bot, _update("/start", update_id=1))
    await dp.feed_update(bot, _update("/unknown", update_id=2))
    await dp.feed_update(bot, _update("hi", chat_type="group", update_id=3))
    assert calls == []
    assert any("DeepSeek" in (getattr(m, "text", "") or "") for m in sent)  # /start answered
