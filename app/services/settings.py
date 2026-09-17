from app.config import load_settings
from app.db.repository import SettingsRepository


_settings = load_settings()
settings_repository = SettingsRepository(
    _settings.database_path,
    database_url=_settings.database_url,
    database_password=_settings.postgres_password,
)
