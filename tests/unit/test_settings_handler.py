import pytest

from app.bot.handlers import settings as settings_handler
from app.db.repository import SettingsRepository


class FakeUser:
    def __init__(self, user_id: int = 5001, language_code: str = "en") -> None:
        self.id = user_id
        self.language_code = language_code


class FakeMessage:
    def __init__(self, chat_type: str = "private", chat_id: int = 50010) -> None:
        self.from_user = FakeUser()
        self.chat = FakeChat(chat_type, chat_id)
        self.answers: list[dict[str, object]] = []

    async def answer(self, text: str, **kwargs: object) -> None:
        self.answers.append({"text": text, **kwargs})


class FakeCallback:
    def __init__(
        self,
        data: str,
        chat_type: str = "private",
        chat_id: int = 50010,
        member_status: str = "administrator",
    ) -> None:
        self.data = data
        self.from_user = FakeUser()
        self.message = FakeEditableMessage(chat_type=chat_type, chat_id=chat_id)
        self.bot = FakeBot(member_status)
        self.answers: list[dict[str, object]] = []

    async def answer(self, text: str | None = None, **kwargs: object) -> None:
        self.answers.append({"text": text, **kwargs})


class FakeBot:
    def __init__(self, member_status: str) -> None:
        self.member_status = member_status

    async def get_chat_member(self, chat_id: int, user_id: int) -> object:
        return FakeChatMember(self.member_status)


class FakeChatMember:
    def __init__(self, status: str) -> None:
        self.status = status


class FakeEditableMessage(FakeMessage):
    def __init__(self, chat_type: str = "private", chat_id: int = 50010) -> None:
        super().__init__(chat_type=chat_type, chat_id=chat_id)
        self.edits: list[dict[str, object]] = []

    async def edit_text(self, text: str, **kwargs: object) -> None:
        self.edits.append({"text": text, **kwargs})


class FakeChat:
    def __init__(self, chat_type: str, chat_id: int) -> None:
        self.type = chat_type
        self.id = chat_id


@pytest.mark.asyncio
async def test_handle_settings_answers_with_keyboard(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        settings_handler,
        "settings_repository",
        SettingsRepository(str(tmp_path / "settings.sqlite3")),
    )
    message = FakeMessage()

    await settings_handler.handle_settings(message)

    assert len(message.answers) == 1
    assert "Settings" in str(message.answers[0]["text"])
    assert message.answers[0]["reply_markup"] is not None


@pytest.mark.asyncio
async def test_handle_settings_callback_toggles_provider(tmp_path, monkeypatch) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    monkeypatch.setattr(settings_handler, "settings_repository", repository)
    callback = FakeCallback("settings:user:map_provider:apple")

    await settings_handler.handle_settings_callback(callback)

    settings = repository.get_user_settings(callback.from_user.id)
    assert "apple" not in settings.favorite_providers
    assert len(callback.message.edits) == 1
    assert callback.answers == [{"text": "Settings updated."}]


@pytest.mark.asyncio
async def test_handle_settings_callback_toggles_navigation_provider(
    tmp_path,
    monkeypatch,
) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    monkeypatch.setattr(settings_handler, "settings_repository", repository)
    callback = FakeCallback("settings:user:navigation_provider:waze")

    await settings_handler.handle_settings_callback(callback)

    settings = repository.get_user_settings(callback.from_user.id)
    assert "waze" not in settings.favorite_navigation_providers
    assert len(callback.message.edits) == 1
    assert callback.answers == [{"text": "Settings updated."}]


@pytest.mark.asyncio
async def test_handle_settings_answers_with_chat_settings_keyboard(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings_handler,
        "settings_repository",
        SettingsRepository(str(tmp_path / "settings.sqlite3")),
    )
    message = FakeMessage(chat_type="supergroup", chat_id=-100123)

    await settings_handler.handle_settings(message)

    assert len(message.answers) == 1
    assert "Chat settings" in str(message.answers[0]["text"])
    assert message.answers[0]["reply_markup"] is not None


@pytest.mark.asyncio
async def test_handle_settings_callback_toggles_chat_provider(
    tmp_path,
    monkeypatch,
) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    monkeypatch.setattr(settings_handler, "settings_repository", repository)
    callback = FakeCallback(
        "settings:chat:map_provider:apple",
        chat_type="supergroup",
        chat_id=-100123,
    )

    await settings_handler.handle_settings_callback(callback)

    settings = repository.get_chat_settings(-100123)
    assert "apple" not in settings.favorite_providers
    assert len(callback.message.edits) == 1
    assert callback.answers == [{"text": "Settings updated."}]


@pytest.mark.asyncio
async def test_handle_settings_callback_toggles_chat_navigation_provider(
    tmp_path,
    monkeypatch,
) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    monkeypatch.setattr(settings_handler, "settings_repository", repository)
    callback = FakeCallback(
        "settings:chat:navigation_provider:waze",
        chat_type="supergroup",
        chat_id=-100123,
    )

    await settings_handler.handle_settings_callback(callback)

    settings = repository.get_chat_settings(-100123)
    assert "waze" not in settings.favorite_navigation_providers
    assert len(callback.message.edits) == 1
    assert callback.answers == [{"text": "Settings updated."}]


@pytest.mark.asyncio
async def test_handle_settings_callback_denies_chat_settings_for_non_admin(
    tmp_path,
    monkeypatch,
) -> None:
    repository = SettingsRepository(str(tmp_path / "settings.sqlite3"))
    monkeypatch.setattr(settings_handler, "settings_repository", repository)
    callback = FakeCallback(
        "settings:chat:map_provider:apple",
        chat_type="supergroup",
        chat_id=-100123,
        member_status="member",
    )

    await settings_handler.handle_settings_callback(callback)

    settings = repository.get_chat_settings(-100123)
    assert "apple" in settings.favorite_providers
    assert callback.message.edits == []
    assert callback.answers == [
        {
            "text": "Only chat administrators can change chat settings.",
            "show_alert": True,
        }
    ]
