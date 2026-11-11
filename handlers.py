"""Telegram message handlers."""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError

from apps.telegram.formatters import safe_edit, send_result
from core.config import Settings
from engine.orchestrator import Stage, translate_historical

logger = logging.getLogger(__name__)

MAX_WORDS = 500
# Process-local on purpose (Phase 1A); moves to durable jobs in a later phase.
active_users: set[int] = set()

START_TEXT = (
    "გამარჯობა! 👋\nმე ვარ მრავალაგენტიანი ისტორიული მთარგმნელი ბოტი.\n"
    "ვმუშაობ <b>DeepSeek</b>-ისა და <b>Gemini</b>-ს მძლავრი სავაჭრო ჰიბრიდით! 🚀"
)
STAGE_TEXT = {
    Stage.TRANSLATE: "⏳ <i>ეტაპი 1/3: DeepSeek Translator ამუშავებს...</i>",
    Stage.REVIEW: "⏳ <i>ეტაპი 2/3: DeepSeek ამოწმებს (Accuracy, Guard, Critic)...</i>",
    Stage.SYNTHESIZE: "⏳ <i>ეტაპი 3/3: Gemini Synthesizer აჯამებს...</i>",
}
BUSY_TEXT = "⏳ წინა მოთხოვნა მუშავდება. გთხოვთ დაელოდოთ."
TOO_LONG_TEXT = "❌ ტექსტი ძალიან გრძელია. გთხოვთ, გამოაგზავნოთ 500 სიტყვაზე ნაკლები."
DENIED_TEXT = "⛔ ამ ბოტზე წვდომა შეზღუდულია."
QUEUED_TEXT = "⏳ <i>რიგში ელოდება...</i>"


def is_allowed(settings: Settings, user_id: int) -> bool:
    return not settings.allowed_user_ids or user_id in settings.allowed_user_ids


def word_count(text: str) -> int:
    return len(text.split())


async def cmd_start(message: types.Message, settings: Settings) -> None:
    if message.from_user is not None and not is_allowed(settings, message.from_user.id):
        await message.answer(DENIED_TEXT)
        return
    await message.answer(START_TEXT)


async def process_translation_request(
    message: types.Message, bot: Bot, settings: Settings, job_slots: asyncio.Semaphore
) -> None:
    if message.from_user is None or not message.text or not message.text.strip():
        return
    user_id = message.from_user.id
    if not is_allowed(settings, user_id):
        logger.info("Rejected request from non-allowlisted user %s", user_id)
        await message.reply(DENIED_TEXT)
        return
    if user_id in active_users:
        await message.reply(BUSY_TEXT)
        return

    raw_text = message.text
    if word_count(raw_text) > MAX_WORDS:
        await message.reply(TOO_LONG_TEXT)
        return

    # No await between the membership check above and this add, so it is race-free.
    active_users.add(user_id)
    status_msg: types.Message | None = None
    try:
        status_msg = await message.reply(
            QUEUED_TEXT if job_slots.locked() else STAGE_TEXT[Stage.TRANSLATE]
        )
        sent = status_msg

        async def on_stage(stage: Stage) -> None:
            await safe_edit(sent, STAGE_TEXT[stage])

        async with job_slots:
            await on_stage(Stage.TRANSLATE)
            try:
                await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            except TelegramAPIError:
                pass
            result = await translate_historical(raw_text, on_stage=on_stage)
        await send_result(message, status_msg, result)

    except AuthenticationError:
        logger.critical("DeepSeek authentication failed - check DEEPSEEK_API_KEY")
        await _report_error(message, status_msg, "❌ DeepSeek-ის API გასაღები არასწორია.")
    except RateLimitError:
        logger.warning("DeepSeek rate limit hit")
        await _report_error(message, status_msg, "❌ სერვისი გადატვირთულია. სცადეთ მოგვიანებით.")
    except (APITimeoutError, APIConnectionError):
        logger.warning("DeepSeek unreachable or timed out", exc_info=True)
        await _report_error(
            message, status_msg, "❌ სერვისი დროებით მიუწვდომელია. სცადეთ მოგვიანებით."
        )
    except Exception:
        logger.exception("Unexpected Telegram handler error")
        await _report_error(message, status_msg, "❌ სისტემური შეცდომა მოხდა.")
    finally:
        active_users.discard(user_id)


async def _report_error(
    message: types.Message, status_msg: types.Message | None, text: str
) -> None:
    if status_msg is not None and await safe_edit(status_msg, text):
        return
    try:
        await message.reply(text)
    except TelegramAPIError:
        logger.warning("Could not deliver error message to user", exc_info=True)


def build_router() -> Router:
    """A fresh router per dispatcher (aiogram routers can only be attached once)."""
    router = Router(name="historical-translator")
    router.message.register(cmd_start, Command("start"), F.chat.type == "private")
    router.message.register(
        process_translation_request, F.text, ~F.text.startswith("/"), F.chat.type == "private"
    )
    return router


def register_handlers(dp: Dispatcher, settings: Settings) -> None:
    dp.workflow_data["settings"] = settings
    dp.workflow_data["job_slots"] = asyncio.Semaphore(settings.max_concurrent_jobs)
    dp.include_router(build_router())
