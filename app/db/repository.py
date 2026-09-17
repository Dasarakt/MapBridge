import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from app.db.connection import connect_postgres
from app.db.models import ChatSettings, UserSettings
from app.db.migrations import LATEST_SCHEMA_VERSION


DEFAULT_PROVIDER_ORDER = (
    "google",
    "yandex",
    "apple",
    "twogis",
    "osm",
    "organic_maps",
    "mapsme",
)

DEFAULT_NAVIGATION_PROVIDER_ORDER = (
    "yandex_navigator",
    "waze",
    "organic_maps",
    "mapsme",
)


class SettingsRepository:
    def __init__(
        self,
        database_path: str = "mapbridge.sqlite3",
        *,
        database_url: str = "",
        database_password: str = "",
    ) -> None:
        self._database_path = database_path
        self._database_url = database_url
        self._database_password = database_password
        self._placeholder = "%s" if database_url else "?"
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        if self._database_url:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT to_regclass('public.schema_migrations') AS table_name"
                ).fetchone()
                if row["table_name"] is None:
                    raise RuntimeError(
                        "PostgreSQL schema is missing; run python -m app.db.migrate"
                    )
                row = connection.execute(
                    "SELECT MAX(version) AS version FROM schema_migrations"
                ).fetchone()
                if row["version"] != LATEST_SCHEMA_VERSION:
                    raise RuntimeError(
                        "PostgreSQL schema is out of date; run python -m app.db.migrate"
                    )
            self._initialized = True
            return

        database_parent = Path(self._database_path).expanduser().parent
        if str(database_parent) not in {"", "."}:
            database_parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    telegram_user_id INTEGER PRIMARY KEY,
                    favorite_providers TEXT NOT NULL,
                    favorite_navigation_providers TEXT NOT NULL,
                    language_code TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_settings (
                    telegram_chat_id INTEGER PRIMARY KEY,
                    favorite_providers TEXT NOT NULL,
                    favorite_navigation_providers TEXT NOT NULL,
                    language_code TEXT
                )
                """
            )
            self._ensure_column(
                connection,
                "user_settings",
                "favorite_navigation_providers",
                json.dumps(list(DEFAULT_NAVIGATION_PROVIDER_ORDER)),
            )
            self._ensure_column(
                connection,
                "chat_settings",
                "favorite_navigation_providers",
                json.dumps(list(DEFAULT_NAVIGATION_PROVIDER_ORDER)),
            )
        self._initialized = True

    def get_user_settings(self, telegram_user_id: int) -> UserSettings:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                f"""
                SELECT favorite_providers, favorite_navigation_providers, language_code
                FROM user_settings
                WHERE telegram_user_id = {self._placeholder}
                """,
                (telegram_user_id,),
            ).fetchone()

        if row is None:
            return UserSettings(
                telegram_user_id=telegram_user_id,
                favorite_providers=DEFAULT_PROVIDER_ORDER,
                favorite_navigation_providers=DEFAULT_NAVIGATION_PROVIDER_ORDER,
            )

        return UserSettings(
            telegram_user_id=telegram_user_id,
            favorite_providers=tuple(json.loads(row["favorite_providers"])),
            favorite_navigation_providers=tuple(
                json.loads(row["favorite_navigation_providers"])
            ),
            language_code=row["language_code"],
        )

    def set_favorite_providers(
        self,
        telegram_user_id: int,
        providers: Iterable[str],
    ) -> UserSettings:
        self.initialize()
        settings = self.get_user_settings(telegram_user_id)
        favorite_providers = tuple(providers)
        self._upsert(
            UserSettings(
                telegram_user_id=telegram_user_id,
                favorite_providers=favorite_providers,
                favorite_navigation_providers=settings.favorite_navigation_providers,
                language_code=settings.language_code,
            )
        )
        return self.get_user_settings(telegram_user_id)

    def set_favorite_navigation_providers(
        self,
        telegram_user_id: int,
        providers: Iterable[str],
    ) -> UserSettings:
        self.initialize()
        settings = self.get_user_settings(telegram_user_id)
        self._upsert(
            UserSettings(
                telegram_user_id=telegram_user_id,
                favorite_providers=settings.favorite_providers,
                favorite_navigation_providers=tuple(providers),
                language_code=settings.language_code,
            )
        )
        return self.get_user_settings(telegram_user_id)

    def toggle_provider(self, telegram_user_id: int, provider: str) -> UserSettings:
        self.initialize()
        settings = self.get_user_settings(telegram_user_id)
        providers = list(settings.favorite_providers)

        if provider in providers:
            providers.remove(provider)
        elif provider in DEFAULT_PROVIDER_ORDER:
            providers.append(provider)
            providers.sort(key=DEFAULT_PROVIDER_ORDER.index)

        return self.set_favorite_providers(telegram_user_id, providers)

    def toggle_navigation_provider(
        self,
        telegram_user_id: int,
        provider: str,
    ) -> UserSettings:
        self.initialize()
        settings = self.get_user_settings(telegram_user_id)
        providers = list(settings.favorite_navigation_providers)

        if provider in providers:
            providers.remove(provider)
        elif provider in DEFAULT_NAVIGATION_PROVIDER_ORDER:
            providers.append(provider)
            providers.sort(key=DEFAULT_NAVIGATION_PROVIDER_ORDER.index)

        return self.set_favorite_navigation_providers(telegram_user_id, providers)

    def set_language(
        self,
        telegram_user_id: int,
        language_code: str | None,
    ) -> UserSettings:
        self.initialize()
        settings = self.get_user_settings(telegram_user_id)
        self._upsert(
            UserSettings(
                telegram_user_id=telegram_user_id,
                favorite_providers=settings.favorite_providers,
                favorite_navigation_providers=settings.favorite_navigation_providers,
                language_code=language_code,
            )
        )
        return self.get_user_settings(telegram_user_id)

    def get_chat_settings(self, telegram_chat_id: int) -> ChatSettings:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                f"""
                SELECT favorite_providers, favorite_navigation_providers, language_code
                FROM chat_settings
                WHERE telegram_chat_id = {self._placeholder}
                """,
                (telegram_chat_id,),
            ).fetchone()

        if row is None:
            return ChatSettings(
                telegram_chat_id=telegram_chat_id,
                favorite_providers=DEFAULT_PROVIDER_ORDER,
                favorite_navigation_providers=DEFAULT_NAVIGATION_PROVIDER_ORDER,
            )

        return ChatSettings(
            telegram_chat_id=telegram_chat_id,
            favorite_providers=tuple(json.loads(row["favorite_providers"])),
            favorite_navigation_providers=tuple(
                json.loads(row["favorite_navigation_providers"])
            ),
            language_code=row["language_code"],
        )

    def set_chat_favorite_providers(
        self,
        telegram_chat_id: int,
        providers: Iterable[str],
    ) -> ChatSettings:
        self.initialize()
        settings = self.get_chat_settings(telegram_chat_id)
        self._upsert_chat(
            ChatSettings(
                telegram_chat_id=telegram_chat_id,
                favorite_providers=tuple(providers),
                favorite_navigation_providers=settings.favorite_navigation_providers,
                language_code=settings.language_code,
            )
        )
        return self.get_chat_settings(telegram_chat_id)

    def set_chat_favorite_navigation_providers(
        self,
        telegram_chat_id: int,
        providers: Iterable[str],
    ) -> ChatSettings:
        self.initialize()
        settings = self.get_chat_settings(telegram_chat_id)
        self._upsert_chat(
            ChatSettings(
                telegram_chat_id=telegram_chat_id,
                favorite_providers=settings.favorite_providers,
                favorite_navigation_providers=tuple(providers),
                language_code=settings.language_code,
            )
        )
        return self.get_chat_settings(telegram_chat_id)

    def toggle_chat_provider(
        self,
        telegram_chat_id: int,
        provider: str,
    ) -> ChatSettings:
        self.initialize()
        settings = self.get_chat_settings(telegram_chat_id)
        providers = list(settings.favorite_providers)

        if provider in providers:
            providers.remove(provider)
        elif provider in DEFAULT_PROVIDER_ORDER:
            providers.append(provider)
            providers.sort(key=DEFAULT_PROVIDER_ORDER.index)

        return self.set_chat_favorite_providers(telegram_chat_id, providers)

    def toggle_chat_navigation_provider(
        self,
        telegram_chat_id: int,
        provider: str,
    ) -> ChatSettings:
        self.initialize()
        settings = self.get_chat_settings(telegram_chat_id)
        providers = list(settings.favorite_navigation_providers)

        if provider in providers:
            providers.remove(provider)
        elif provider in DEFAULT_NAVIGATION_PROVIDER_ORDER:
            providers.append(provider)
            providers.sort(key=DEFAULT_NAVIGATION_PROVIDER_ORDER.index)

        return self.set_chat_favorite_navigation_providers(
            telegram_chat_id,
            providers,
        )

    def set_chat_language(
        self,
        telegram_chat_id: int,
        language_code: str | None,
    ) -> ChatSettings:
        self.initialize()
        settings = self.get_chat_settings(telegram_chat_id)
        self._upsert_chat(
            ChatSettings(
                telegram_chat_id=telegram_chat_id,
                favorite_providers=settings.favorite_providers,
                favorite_navigation_providers=settings.favorite_navigation_providers,
                language_code=language_code,
            )
        )
        return self.get_chat_settings(telegram_chat_id)

    def _upsert(self, settings: UserSettings) -> None:
        with self._connect() as connection:
            connection.execute(
                f"""
                INSERT INTO user_settings (
                    telegram_user_id,
                    favorite_providers,
                    favorite_navigation_providers,
                    language_code
                )
                VALUES ({', '.join((self._placeholder,) * 4)})
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    favorite_providers = excluded.favorite_providers,
                    favorite_navigation_providers = excluded.favorite_navigation_providers,
                    language_code = excluded.language_code
                """,
                (
                    settings.telegram_user_id,
                    json.dumps(list(settings.favorite_providers)),
                    json.dumps(list(settings.favorite_navigation_providers)),
                    settings.language_code,
                ),
            )

    def _upsert_chat(self, settings: ChatSettings) -> None:
        with self._connect() as connection:
            connection.execute(
                f"""
                INSERT INTO chat_settings (
                    telegram_chat_id,
                    favorite_providers,
                    favorite_navigation_providers,
                    language_code
                )
                VALUES ({', '.join((self._placeholder,) * 4)})
                ON CONFLICT(telegram_chat_id) DO UPDATE SET
                    favorite_providers = excluded.favorite_providers,
                    favorite_navigation_providers = excluded.favorite_navigation_providers,
                    language_code = excluded.language_code
                """,
                (
                    settings.telegram_chat_id,
                    json.dumps(list(settings.favorite_providers)),
                    json.dumps(list(settings.favorite_navigation_providers)),
                    settings.language_code,
                ),
            )

    def _connect(self):
        if self._database_url:
            from psycopg.rows import dict_row

            return connect_postgres(
                self._database_url,
                self._database_password,
                row_factory=dict_row,
            )
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_column(
        self,
        connection: sqlite3.Connection,
        table: str,
        column: str,
        default_value: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column in columns:
            return

        escaped_default = default_value.replace("'", "''")
        connection.execute(
            f"ALTER TABLE {table} "
            f"ADD COLUMN {column} TEXT NOT NULL DEFAULT '{escaped_default}'"
        )
