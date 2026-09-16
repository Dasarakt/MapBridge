from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app.bot.i18n import message_text_with_settings
from app.bot.keyboards.maps import build_map_links_keyboard
from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.services.conversion import LocationConverter, create_default_converter
from app.services.settings import settings_repository


router = Router()
converter: LocationConverter = create_default_converter()


def _get_user_id(message: Message) -> int | None:
    user = message.from_user
    return user.id if user is not None else None


def _is_group_chat(message: Message) -> bool:
    return message.chat.type in {"group", "supergroup"}


def _is_shared_chat(message: Message) -> bool:
    return message.chat.type in {"group", "supergroup", "channel"}


async def answer_with_map_links(message: Message, location: Location) -> None:
    if _is_shared_chat(message):
        user_settings = settings_repository.get_chat_settings(message.chat.id)
    else:
        user_id = _get_user_id(message)
        user_settings = (
            settings_repository.get_user_settings(user_id)
            if user_id is not None
            else None
        )
    view_provider_names = (
        user_settings.favorite_providers if user_settings is not None else None
    )
    navigation_provider_names = (
        user_settings.favorite_navigation_providers
        if user_settings is not None
        else None
    )
    language_code = user_settings.language_code if user_settings is not None else None
    all_links = converter.get_links(location)
    links = [
        *converter.get_links(
            location,
            provider_names=view_provider_names,
            action="view",
        ),
        *converter.get_links(
            location,
            provider_names=navigation_provider_names,
            action="navigate",
        ),
    ]
    if not links:
        links = all_links

    keyboard = build_map_links_keyboard(
        links,
        all_links=all_links,
        location=location,
        all_maps_text=message_text_with_settings(message, "all_maps", language_code),
    )
    answer_kwargs: dict[str, object] = {"reply_markup": keyboard}
    if _is_group_chat(message):
        answer_kwargs["reply_to_message_id"] = message.message_id

    await message.answer(
        f"📍 {location.latitude:.7f}, {location.longitude:.7f}",
        **answer_kwargs,
    )


@router.message(F.text)
@router.channel_post(F.text)
async def handle_text_location(message: Message) -> None:
    if message.text is None:
        return

    try:
        location = await converter.parse(message.text)
    except MapBridgeError:
        if _is_shared_chat(message):
            return

        user_id = _get_user_id(message)
        user_settings = (
            settings_repository.get_user_settings(user_id)
            if user_id is not None
            else None
        )
        language_code = (
            user_settings.language_code if user_settings is not None else None
        )
        await message.answer(
            message_text_with_settings(message, "unsupported_location", language_code)
        )
        return

    await answer_with_map_links(message, location)


@router.message(F.location)
@router.channel_post(F.location)
async def handle_telegram_location(message: Message) -> None:
    if message.location is None:
        return

    location = Location(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
        source="telegram_location",
    )
    await answer_with_map_links(message, location)


@router.callback_query(F.data.startswith("maps_all:"))
async def handle_all_maps(callback: CallbackQuery) -> None:
    if callback.data is None or callback.message is None:
        return

    _, latitude, longitude = callback.data.split(":", maxsplit=2)
    location = Location(latitude=float(latitude), longitude=float(longitude))
    links = converter.get_links(location)
    keyboard = build_map_links_keyboard(links)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "maps_noop")
async def handle_maps_noop(callback: CallbackQuery) -> None:
    await callback.answer()
