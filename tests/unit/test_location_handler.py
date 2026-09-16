import pytest

from app.bot.handlers import location as location_handler
from app.bot.handlers.location import handle_telegram_location, handle_text_location
from app.db.repository import SettingsRepository


class FakeUser:
    def __init__(self, language_code: str | None, user_id: int = 1002) -> None:
        self.id = user_id
        self.language_code = language_code


class FakeMessage:
    def __init__(
        self,
        text: str | None = None,
        location: object | None = None,
        language_code: str | None = "ru",
        chat_type: str = "private",
        message_id: int = 77,
        chat_id: int = 10020,
    ) -> None:
        self.text = text
        self.location = location
        self.from_user = FakeUser(language_code)
        self.chat = FakeChat(chat_type, chat_id)
        self.message_id = message_id
        self.answers: list[dict[str, object]] = []

    async def answer(self, text: str, **kwargs: object) -> None:
        self.answers.append({"text": text, **kwargs})


class FakeChat:
    def __init__(self, chat_type: str, chat_id: int) -> None:
        self.type = chat_type
        self.id = chat_id


@pytest.mark.asyncio
async def test_handle_text_location_answers_with_coordinates_and_keyboard() -> None:
    message = FakeMessage("42.4439296, 42.3915008")

    await handle_text_location(message)

    assert len(message.answers) == 1
    answer = message.answers[0]
    assert answer["text"] == "📍 42.4439296, 42.3915008"
    assert answer["reply_markup"] is not None


@pytest.mark.asyncio
async def test_handle_text_location_answers_unsupported_input() -> None:
    message = FakeMessage("hello world")

    await handle_text_location(message)

    assert len(message.answers) == 1
    assert "Не смог распознать геолокацию" in str(message.answers[0]["text"])


@pytest.mark.asyncio
async def test_handle_text_location_answers_unsupported_input_in_english() -> None:
    message = FakeMessage("hello world", language_code="en")

    await handle_text_location(message)

    assert len(message.answers) == 1
    assert "I could not recognize the location" in str(message.answers[0]["text"])


@pytest.mark.asyncio
async def test_handle_text_location_is_silent_for_unsupported_group_input() -> None:
    message = FakeMessage("hello world", chat_type="supergroup")

    await handle_text_location(message)

    assert message.answers == []


@pytest.mark.asyncio
async def test_handle_text_location_replies_to_group_location_message() -> None:
    message = FakeMessage(
        "42.4439296, 42.3915008",
        chat_type="group",
        message_id=123,
    )

    await handle_text_location(message)

    assert len(message.answers) == 1
    answer = message.answers[0]
    assert answer["text"] == "📍 42.4439296, 42.3915008"
    assert answer["reply_to_message_id"] == 123


@pytest.mark.asyncio
async def test_handle_text_location_uses_chat_settings_in_group(
    tmp_path,
    monkeypatch,
) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    repository.set_chat_favorite_providers(-100123, ("google",))
    monkeypatch.setattr(location_handler, "settings_repository", repository)
    message = FakeMessage(
        "42.4439296, 42.3915008",
        chat_type="supergroup",
        chat_id=-100123,
    )

    await handle_text_location(message)

    keyboard = message.answers[0]["reply_markup"]
    visible_buttons = [
        button.text
        for row in keyboard.inline_keyboard
        for button in row
    ]
    assert "Google Maps" in visible_buttons
    assert "Yandex Maps" not in visible_buttons
    assert "Все карты" in visible_buttons


class FakeTelegramLocation:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude


@pytest.mark.asyncio
async def test_handle_telegram_location_answers_with_coordinates_and_keyboard() -> None:
    message = FakeMessage(
        location=FakeTelegramLocation(latitude=42.4439296, longitude=42.3915008)
    )

    await handle_telegram_location(message)

    assert len(message.answers) == 1
    answer = message.answers[0]
    assert answer["text"] == "📍 42.4439296, 42.3915008"
    assert answer["reply_markup"] is not None
