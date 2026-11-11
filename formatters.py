"""Telegram output formatting and long-result file delivery."""
import html
import logging

from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import BufferedInputFile, Message

from engine.result import TranslationResult

logger = logging.getLogger(__name__)

TELEGRAM_MSG_LIMIT = 4096


async def safe_edit(status_msg: Message, text: str) -> bool:
    """Edit a status message; UI failures (deleted message, unchanged text) are non-fatal."""
    try:
        await status_msg.edit_text(text)
        return True
    except TelegramAPIError as exc:
        logger.debug("Status edit skipped: %s", exc)
        return False


async def send_result(message: Message, status_msg: Message,
                      result: TranslationResult) -> None:
    escaped_translation = html.escape(result.final_translation)
    escaped_summary = html.escape(result.summary)
    issues_list = "\n".join(
        f"• {html.escape(issue)}" for issue in result.issues_fixed
    ) or "• ხარვეზები არ დაფიქსირებულა."

    response_text = (
        f"✨ <b>დამუშავებული თარგმანი:</b>\n{escaped_translation}\n\n"
        f"📊 <b>სანდოობა:</b> {result.confidence_score}%\n"
        f"🛠 <b>გასწორებული საკითხები:</b>\n{issues_list}\n\n"
        f"📝 <b>სინთეზის რეპორტი:</b> {escaped_summary}"
    )

    if len(response_text) <= TELEGRAM_MSG_LIMIT:
        try:
            await status_msg.edit_text(response_text)
            return
        except TelegramBadRequest:
            pass

    await safe_edit(
        status_msg,
        "✅ თარგმანი დასრულებულია (ტექსტი გრძელია სრულად საჩვენებლად).\n"
        f"📊 <b>სანდოობა:</b> {result.confidence_score}%\n"
        f"📝 <b>რეპორტი:</b> {escaped_summary}",
    )

    document = BufferedInputFile(
        result.final_translation.encode("utf-8"),
        filename="historical_translation.txt",
    )
    await message.answer_document(document, caption="სრული თარგმანი ფაილში 👆")
