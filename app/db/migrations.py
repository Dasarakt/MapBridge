MIGRATIONS = {
    1: (
        """
        CREATE TABLE user_settings (
            telegram_user_id BIGINT PRIMARY KEY,
            favorite_providers TEXT NOT NULL,
            favorite_navigation_providers TEXT NOT NULL,
            language_code TEXT
        )
        """,
        """
        CREATE TABLE chat_settings (
            telegram_chat_id BIGINT PRIMARY KEY,
            favorite_providers TEXT NOT NULL,
            favorite_navigation_providers TEXT NOT NULL,
            language_code TEXT
        )
        """,
    ),
}

LATEST_SCHEMA_VERSION = max(MIGRATIONS)
