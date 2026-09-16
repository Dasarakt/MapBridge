from app.bot.i18n import normalize_language, translate


def test_normalize_language_accepts_supported_language() -> None:
    assert normalize_language("ru") == "ru"
    assert normalize_language("en") == "en"


def test_normalize_language_uses_base_language_from_locale() -> None:
    assert normalize_language("ru-RU") == "ru"
    assert normalize_language("en_US") == "en"


def test_normalize_language_falls_back_to_english() -> None:
    assert normalize_language(None) == "en"
    assert normalize_language("ka") == "en"


def test_translate_returns_language_text() -> None:
    assert "MapBridge converts" in translate("start", "en")
    assert "MapBridge превращает" in translate("start", "ru")

