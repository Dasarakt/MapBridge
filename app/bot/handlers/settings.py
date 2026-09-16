from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.i18n import get_message_language_with_settings, message_text_with_settings
from app.bot.keyboards.settings import build_settings_keyboard
from app.services.settings import settings_repository


router = Router()


def _settings_text(message: Message, language_code: str | None) -> str:
    title_key = "settings_title" if _is_private_chat(message) else "chat_settings_title"
    return (
        f"{message_text_with_settings(message, title_key, language_code)}\n\n"
        f"{message_text_with_settings(message, 'settings_maps', language_code)}\n"
        f"{message_text_with_settings(message, 'settings_navigation', language_code)}\n"
        f"{message_text_with_settings(message, 'settings_language', language_code)}"
    )


def _get_message_user_id(message: Message) -> int | None:
    user = message.from_user
    return user.id if user is not None else None


def _is_private_chat(message: Message) -> bool:
    return message.chat.type == "private"


def _settings_scope(message: Message) -> str:
    return "user" if _is_private_chat(message) else "chat"


def _status_value(status: object) -> str:
    value = getattr(status, "value", status)
    return str(value)


async def _can_update_chat_settings(callback: CallbackQuery) -> bool:
    if callback.message is None or callback.from_user is None:
        return False

    member = await callback.bot.get_chat_member(
        callback.message.chat.id,
        callback.from_user.id,
    )
    return _status_value(member.status) in {"creator", "administrator"}


@router.message(Command("settings"))
@router.channel_post(Command("settings"))
async def handle_settings(message: Message) -> None:
    scope = _settings_scope(message)
    if scope == "user":
        user_id = _get_message_user_id(message)
        if user_id is None:
            return
        settings = settings_repository.get_user_settings(user_id)
    else:
        settings = settings_repository.get_chat_settings(message.chat.id)

    language = get_message_language_with_settings(message, settings.language_code)
    await message.answer(
        _settings_text(message, settings.language_code),
        reply_markup=build_settings_keyboard(settings, language, scope=scope),
    )


@router.callback_query(F.data.startswith("settings:"))
async def handle_settings_callback(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None or callback.from_user is None:
        return

    parts = callback.data.split(":", maxsplit=3)
    if len(parts) != 4:
        return

    _, scope, action, value = parts
    message = callback.message
    if scope == "user":
        user_id = callback.from_user.id
        if action in {"provider", "map_provider"}:
            settings = settings_repository.toggle_provider(user_id, value)
        elif action == "navigation_provider":
            settings = settings_repository.toggle_navigation_provider(user_id, value)
        elif action == "language":
            settings = settings_repository.set_language(
                user_id,
                None if value == "auto" else value,
            )
        else:
            return
    elif scope == "chat":
        if not await _can_update_chat_settings(callback):
            await callback.answer(
                message_text_with_settings(message, "settings_admin_required", None),
                show_alert=True,
            )
            return

        chat_id = message.chat.id
        if action in {"provider", "map_provider"}:
            settings = settings_repository.toggle_chat_provider(chat_id, value)
        elif action == "navigation_provider":
            settings = settings_repository.toggle_chat_navigation_provider(chat_id, value)
        elif action == "language":
            settings = settings_repository.set_chat_language(
                chat_id,
                None if value == "auto" else value,
            )
        else:
            return
    else:
        return

    language = get_message_language_with_settings(message, settings.language_code)
    await message.edit_text(
        _settings_text(message, settings.language_code),
        reply_markup=build_settings_keyboard(settings, language, scope=scope),
    )
    await callback.answer(message_text_with_settings(message, "settings_saved", settings.language_code))
