from aiogram.types import Message


DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en", "ru"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "start": (
            "MapBridge converts locations into links for different map services. "
            "Send decimal coordinates to get map buttons."
        ),
        "help": (
            "Send coordinates, a map link, a Plus Code, or a Telegram Location. "
            "Use /settings to choose favorite maps and language."
        ),
        "unsupported_location": (
            "I could not recognize the location. Send coordinates, a map link, "
            "a Plus Code, or a Telegram Location. Example: 41.890210, 12.492231"
        ),
        "all_maps": "All maps",
        "settings_title": "Settings",
        "chat_settings_title": "Chat settings",
        "settings_maps": "Favorite maps",
        "settings_navigation": "Favorite navigation apps",
        "settings_language": "Language",
        "settings_auto_language": "Auto",
        "settings_saved": "Settings updated.",
        "settings_admin_required": "Only chat administrators can change chat settings.",
    },
    "ru": {
        "start": (
            "MapBridge превращает геолокацию в ссылки для разных карт. "
            "Отправь обычные координаты, чтобы получить кнопки карт."
        ),
        "help": (
            "Отправь координаты, ссылку карты, Plus Code или Telegram Location. "
            "В /settings можно выбрать любимые карты и язык."
        ),
        "unsupported_location": (
            "Не смог распознать геолокацию. Отправь координаты, ссылку карты, "
            "Plus Code или Telegram Location. Например: 41.890210, 12.492231"
        ),
        "all_maps": "Все карты",
        "settings_title": "Настройки",
        "chat_settings_title": "Настройки чата",
        "settings_maps": "Любимые карты",
        "settings_navigation": "Любимые навигаторы",
        "settings_language": "Язык",
        "settings_auto_language": "Авто",
        "settings_saved": "Настройки обновлены.",
        "settings_admin_required": "Настройки чата могут менять только администраторы.",
    },
}


def normalize_language(language_code: str | None) -> str:
    if not language_code:
        return DEFAULT_LANGUAGE

    language = language_code.split("-", maxsplit=1)[0].split("_", maxsplit=1)[0]
    if language in SUPPORTED_LANGUAGES:
        return language

    return DEFAULT_LANGUAGE


def get_message_language(message: Message) -> str:
    user = message.from_user
    language_code = user.language_code if user is not None else None
    return normalize_language(language_code)


def get_message_language_with_settings(message: Message, language_code: str | None) -> str:
    if language_code is not None:
        return normalize_language(language_code)

    return get_message_language(message)


def translate(key: str, language: str) -> str:
    return TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE]).get(
        key,
        TRANSLATIONS[DEFAULT_LANGUAGE][key],
    )


def message_text(message: Message, key: str) -> str:
    return translate(key, get_message_language(message))


def message_text_with_settings(
    message: Message,
    key: str,
    language_code: str | None,
) -> str:
    return translate(key, get_message_language_with_settings(message, language_code))
