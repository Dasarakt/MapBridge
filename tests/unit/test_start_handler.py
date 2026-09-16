import pytest

from app.bot.handlers.start import handle_help, handle_start


class FakeUser:
    def __init__(self, language_code: str | None, user_id: int = 1001) -> None:
        self.id = user_id
        self.language_code = language_code


class FakeMessage:
    def __init__(self, language_code: str | None = "ru") -> None:
        self.from_user = FakeUser(language_code)
        self.answers: list[str] = []

    async def answer(self, text: str, **kwargs: object) -> None:
        self.answers.append(text)


@pytest.mark.asyncio
async def test_handle_start_answers_in_russian() -> None:
    message = FakeMessage()

    await handle_start(message)

    assert len(message.answers) == 1
    assert "превращает геолокацию" in message.answers[0]
    assert "Отправь обычные координаты" in message.answers[0]


@pytest.mark.asyncio
async def test_handle_help_answers_in_russian() -> None:
    message = FakeMessage()

    await handle_help(message)

    assert len(message.answers) == 1
    assert "Отправь координаты" in message.answers[0]
    assert "/settings" in message.answers[0]


@pytest.mark.asyncio
async def test_handle_start_answers_in_english_for_english_user() -> None:
    message = FakeMessage(language_code="en")

    await handle_start(message)

    assert len(message.answers) == 1
    assert "converts locations" in message.answers[0]
    assert "Send decimal coordinates" in message.answers[0]


@pytest.mark.asyncio
async def test_handle_help_falls_back_to_english_for_unknown_language() -> None:
    message = FakeMessage(language_code="ka")

    await handle_help(message)

    assert len(message.answers) == 1
    assert "Send coordinates" in message.answers[0]
