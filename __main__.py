"""Telegram polling entry point."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apps.telegram.handlers import register_handlers
from core.config import get_settings
from core.logging_config import configure_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    register_handlers(dispatcher, settings)
    try:
        # Polling cannot coexist with a configured webhook.
        await bot.delete_webhook(drop_pending_updates=False)
        me = await bot.get_me()  # fails fast on an invalid BOT_TOKEN
        logger.info("Starting polling as @%s (access: %s)", me.username,
                    "allowlist" if settings.allowed_user_ids else "open")
        await dispatcher.start_polling(
            bot, allowed_updates=dispatcher.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
