import sqlite3

from app.db.repository import (
    DEFAULT_NAVIGATION_PROVIDER_ORDER,
    DEFAULT_PROVIDER_ORDER,
    SettingsRepository,
)


def test_settings_repository_returns_defaults_for_new_user(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.get_user_settings(telegram_user_id=123)

    assert settings.telegram_user_id == 123
    assert settings.favorite_providers == DEFAULT_PROVIDER_ORDER
    assert settings.favorite_navigation_providers == DEFAULT_NAVIGATION_PROVIDER_ORDER
    assert settings.language_code is None


def test_settings_repository_persists_provider_toggle(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.toggle_provider(telegram_user_id=123, provider="apple")

    assert "apple" not in settings.favorite_providers

    reloaded = SettingsRepository(str(tmp_path / "settings.sqlite3")).get_user_settings(
        telegram_user_id=123
    )

    assert "apple" not in reloaded.favorite_providers


def test_settings_repository_persists_navigation_provider_toggle(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.toggle_navigation_provider(
        telegram_user_id=123,
        provider="waze",
    )

    assert "waze" not in settings.favorite_navigation_providers

    reloaded = SettingsRepository(str(tmp_path / "settings.sqlite3")).get_user_settings(
        telegram_user_id=123
    )

    assert "waze" not in reloaded.favorite_navigation_providers


def test_settings_repository_persists_language(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.set_language(telegram_user_id=123, language_code="ru")

    assert settings.language_code == "ru"

    settings = repository.set_language(telegram_user_id=123, language_code=None)

    assert settings.language_code is None


def test_settings_repository_migrates_existing_user_settings_database(tmp_path) -> None:
    database_path = tmp_path / "settings.sqlite3"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE user_settings (
                telegram_user_id INTEGER PRIMARY KEY,
                favorite_providers TEXT NOT NULL,
                language_code TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO user_settings (
                telegram_user_id,
                favorite_providers,
                language_code
            )
            VALUES (123, '["google"]', 'ru')
            """
        )

    settings = SettingsRepository(str(database_path)).get_user_settings(
        telegram_user_id=123
    )

    assert settings.favorite_providers == ("google",)
    assert settings.favorite_navigation_providers == DEFAULT_NAVIGATION_PROVIDER_ORDER
    assert settings.language_code == "ru"


def test_settings_repository_persists_chat_provider_toggle(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.toggle_chat_provider(telegram_chat_id=-100123, provider="apple")

    assert "apple" not in settings.favorite_providers

    reloaded = SettingsRepository(str(tmp_path / "settings.sqlite3")).get_chat_settings(
        telegram_chat_id=-100123
    )

    assert "apple" not in reloaded.favorite_providers


def test_settings_repository_persists_chat_navigation_provider_toggle(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.toggle_chat_navigation_provider(
        telegram_chat_id=-100123,
        provider="waze",
    )

    assert "waze" not in settings.favorite_navigation_providers

    reloaded = SettingsRepository(str(tmp_path / "settings.sqlite3")).get_chat_settings(
        telegram_chat_id=-100123
    )

    assert "waze" not in reloaded.favorite_navigation_providers


def test_settings_repository_persists_chat_language(tmp_path) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))

    settings = repository.set_chat_language(telegram_chat_id=-100123, language_code="ru")

    assert settings.language_code == "ru"
