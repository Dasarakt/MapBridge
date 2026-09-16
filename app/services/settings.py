from app.config import load_settings
from app.db.repository import SettingsRepository


settings_repository = SettingsRepository(load_settings().database_path)
