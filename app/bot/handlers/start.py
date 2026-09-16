from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.i18n import message_text_with_settings
from app.services.settings import settings_repository


router = Router()


def _get_language_code(message: Message) -> str | None:
    user = message.from_user
    if user is None:
        return None

    return settings_repository.get_user_settings(user.id).language_code


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await message.answer(message_text_with_settings(message, "start", _get_language_code(message)))


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(message_text_with_settings(message, "help", _get_language_code(message)))
