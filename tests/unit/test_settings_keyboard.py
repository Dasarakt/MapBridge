from app.bot.keyboards.settings import build_settings_keyboard
from app.db.models import ChatSettings, UserSettings


def test_build_settings_keyboard_marks_selected_values() -> None:
    keyboard = build_settings_keyboard(
        UserSettings(
            telegram_user_id=123,
            favorite_providers=("google", "yandex"),
            favorite_navigation_providers=("waze",),
            language_code="ru",
        ),
        language="ru",
    )

    button_texts = [
        button.text
        for row in keyboard.inline_keyboard
        for button in row
    ]

    assert "✓ Google Maps" in button_texts
    assert "  Apple Maps" in button_texts
    assert "✓ Waze" in button_texts
    assert "  Yandex Navigator" in button_texts
    assert "✓ Русский" in button_texts


def test_build_settings_keyboard_uses_scope_in_callback_data() -> None:
    keyboard = build_settings_keyboard(
        ChatSettings(
            telegram_chat_id=-100123,
            favorite_providers=("google",),
            favorite_navigation_providers=("waze",),
            language_code=None,
        ),
        language="en",
        scope="chat",
    )

    callback_data = [
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
    ]

    assert "settings:chat:map_provider:google" in callback_data
    assert "settings:chat:navigation_provider:waze" in callback_data
    assert "settings:chat:language:auto" in callback_data
