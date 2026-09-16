import asyncio
import logging

from aiogram import Bot, Dispatcher

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


async def _run_bot() -> None:
    settings = load_settings()
    logging.basicConfig(level=settings.log_level)
    settings_repository.initialize()

    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


def run_bot() -> None:
    asyncio.run(_run_bot())
