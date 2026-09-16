from dataclasses import dataclass
import os

from dotenv import find_dotenv, load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    log_level: str = "INFO"
    database_path: str = "mapbridge.sqlite3"
    google_places_api_key: str = ""


def load_settings() -> Settings:
    load_dotenv(find_dotenv(usecwd=True))
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        database_path=os.getenv("DATABASE_PATH", "mapbridge.sqlite3"),
        google_places_api_key=(
            os.getenv("GOOGLE_PLACES_API_KEY", "")
            or os.getenv("GOOGLE_MAPS_API_KEY", "")
        ),
    )
