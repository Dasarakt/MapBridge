from app.config import load_settings


def test_load_settings_reads_telegram_bot_token_from_dotenv(
    tmp_path,
    monkeypatch,
) -> None:
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text(
        "TELEGRAM_BOT_TOKEN=token-from-dotenv\n"
        "LOG_LEVEL=DEBUG\n"
        "GOOGLE_PLACES_API_KEY=places-key\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)

    settings = load_settings()

    assert settings.telegram_bot_token == "token-from-dotenv"
    assert settings.log_level == "DEBUG"
    assert settings.google_places_api_key == "places-key"
