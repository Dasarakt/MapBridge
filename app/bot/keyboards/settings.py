from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n import translate
from app.db.models import ChatSettings, UserSettings
from app.db.repository import DEFAULT_NAVIGATION_PROVIDER_ORDER, DEFAULT_PROVIDER_ORDER
from app.services.conversion import default_providers


def build_settings_keyboard(
    settings: UserSettings | ChatSettings,
    language: str,
    scope: str = "user",
) -> InlineKeyboardMarkup:
    provider_titles = {provider.name: provider.title for provider in default_providers()}
    favorite_providers = set(settings.favorite_providers)
    favorite_navigation_providers = set(settings.favorite_navigation_providers)

    provider_rows = [
        [
            InlineKeyboardButton(
                text=(
                    f"{'✓' if provider_name in favorite_providers else ' '} "
                    f"{provider_titles[provider_name]}"
                ),
                callback_data=f"settings:{scope}:map_provider:{provider_name}",
            )
        ]
        for provider_name in DEFAULT_PROVIDER_ORDER
    ]
    navigation_rows = [
        [
            InlineKeyboardButton(
                text=(
                    f"{'✓' if provider_name in favorite_navigation_providers else ' '} "
                    f"{provider_titles[provider_name]}"
                ),
                callback_data=f"settings:{scope}:navigation_provider:{provider_name}",
            )
        ]
        for provider_name in DEFAULT_NAVIGATION_PROVIDER_ORDER
    ]
    language_rows = [
        [
            InlineKeyboardButton(
                text=(
                    f"{'✓' if settings.language_code is None else ' '} "
                    f"{translate('settings_auto_language', language)}"
                ),
                callback_data=f"settings:{scope}:language:auto",
            ),
            InlineKeyboardButton(
                text=f"{'✓' if settings.language_code == 'en' else ' '} English",
                callback_data=f"settings:{scope}:language:en",
            ),
            InlineKeyboardButton(
                text=f"{'✓' if settings.language_code == 'ru' else ' '} Русский",
                callback_data=f"settings:{scope}:language:ru",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=provider_rows + navigation_rows + language_rows)
