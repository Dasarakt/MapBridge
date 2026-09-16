from dataclasses import dataclass


@dataclass(frozen=True)
class UserSettings:
    telegram_user_id: int
    favorite_providers: tuple[str, ...]
    favorite_navigation_providers: tuple[str, ...]
    language_code: str | None = None


@dataclass(frozen=True)
class ChatSettings:
    telegram_chat_id: int
    favorite_providers: tuple[str, ...]
    favorite_navigation_providers: tuple[str, ...]
    language_code: str | None = None
