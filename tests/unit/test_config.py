from app.config import load_settings


def test_load_settings_reads_telegram_bot_token_from_dotenv(
    tmp_path,
    monkeypatch,
) -> None:
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text(
        "TELEGRAM_BOT_TOKEN=token-from-dotenv\n"
        "LOG_LEVEL=DEBUG\n"
        "DATABASE_URL=postgresql://mapbridge@postgres:5432/mapbridge\n"
        "POSTGRES_PASSWORD=example\n"
        "GOOGLE_PLACES_API_KEY=places-key\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)

    settings = load_settings()

    assert settings.telegram_bot_token == "token-from-dotenv"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://mapbridge@postgres:5432/mapbridge"
    assert settings.postgres_password == "example"
    assert settings.google_places_api_key == "places-key"
    assert "token-from-dotenv" not in repr(settings)
    assert "places-key" not in repr(settings)
    assert "example" not in repr(settings)
    assert "postgresql://" not in repr(settings)
