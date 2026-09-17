import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

from app.bot.handlers.location import router as location_router
from app.bot.handlers.settings import router as settings_router
from app.bot.handlers.start import router as start_router
from app.config import load_settings
from app.services.settings import settings_repository


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(start_router)
    dispatcher.include_router(settings_router)
    dispatcher.include_router(location_router)
    return dispatcher


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class TokenSafeAiohttpSession(AiohttpSession):
    async def make_request(self, bot, method, timeout=None):
        try:
            return await super().make_request(bot, method, timeout)
        except TelegramNetworkError as exc:
            if bot.token not in exc.message:
                raise
            safe_message = exc.message.replace(bot.token, "[REDACTED]")
            raise TelegramNetworkError(method=method, message=safe_message) from None


async def _run_bot() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    settings_repository.initialize()

    bot = Bot(token=settings.telegram_bot_token, session=TokenSafeAiohttpSession())
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


def run_bot() -> None:
    asyncio.run(_run_bot())
