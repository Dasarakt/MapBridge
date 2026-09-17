import asyncio
import os
from urllib.parse import urlsplit

import psycopg
import pytest

from app.bot import app as bot_app
from app.config import Settings
from app.db.connection import connect_postgres
from app.db.migrate import migrate
from app.db.repository import SettingsRepository


@pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)
def test_postgres_migration_and_settings_persist(monkeypatch, caplog) -> None:
    database_url = os.environ["TEST_DATABASE_URL"]
    if urlsplit(database_url).path != "/mapbridge_test":
        pytest.fail("TEST_DATABASE_URL must use the disposable mapbridge_test database")
    password = os.getenv("TEST_POSTGRES_PASSWORD", "")
    wrong_password = "wrong-test-password"
    with pytest.raises(psycopg.OperationalError) as error:
        connect_postgres(database_url, wrong_password)
    assert wrong_password not in str(error.value)
    assert wrong_password not in caplog.text

    migrate(database_url, password)
    migrate(database_url, password)

    with connect_postgres(database_url, password) as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
    assert versions == [(1,)]

    repository = SettingsRepository(
        database_url=database_url,
        database_password=password,
    )
    assert repository.set_language(987654321, "ru").language_code == "ru"
    assert repository.set_favorite_providers(987654321, ("google",)).favorite_providers == (
        "google",
    )
    assert repository.set_favorite_navigation_providers(
        987654321, ("yandex_navigator",)
    ).favorite_navigation_providers == ("yandex_navigator",)
    assert repository.set_chat_language(-100987654321, "en").language_code == "en"
    assert repository.set_chat_favorite_providers(
        -100987654321, ("yandex",)
    ).favorite_providers == ("yandex",)
    assert repository.set_chat_favorite_navigation_providers(
        -100987654321, ("waze",)
    ).favorite_navigation_providers == ("waze",)

    reloaded = SettingsRepository(
        database_url=database_url,
        database_password=password,
    )
    user = reloaded.get_user_settings(987654321)
    chat = reloaded.get_chat_settings(-100987654321)
    assert user.language_code == "ru"
    assert user.favorite_providers == ("google",)
    assert user.favorite_navigation_providers == ("yandex_navigator",)
    assert chat.language_code == "en"
    assert chat.favorite_providers == ("yandex",)
    assert chat.favorite_navigation_providers == ("waze",)

    with connect_postgres(database_url, password) as connection:
        connection.execute("DELETE FROM schema_migrations WHERE version = 1")
    try:
        outdated = SettingsRepository(
            database_url=database_url,
            database_password=password,
        )
        with pytest.raises(RuntimeError, match="out of date"):
            outdated.initialize()

        monkeypatch.setattr(bot_app, "settings_repository", outdated)
        monkeypatch.setattr(
            bot_app,
            "load_settings",
            lambda: Settings(telegram_bot_token="test-token"),
        )
        with pytest.raises(RuntimeError, match="out of date"):
            asyncio.run(bot_app._run_bot())
    finally:
        with connect_postgres(database_url, password) as connection:
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (1) "
                "ON CONFLICT (version) DO NOTHING"
            )

    migrate(database_url, password)
