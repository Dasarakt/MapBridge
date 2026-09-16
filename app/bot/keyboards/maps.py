from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.location import Location
from app.providers.base import MapLink


def build_map_links_keyboard(
    links: list[MapLink],
    all_links: list[MapLink] | None = None,
    location: Location | None = None,
    all_maps_text: str = "All maps",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    actions = tuple(dict.fromkeys(link.action for link in links))

    if len(actions) > 1:
        for action in actions:
            action_links = [link for link in links if link.action == action]
            if not action_links:
                continue

            rows.append(
                [
                    InlineKeyboardButton(
                        text="View" if action == "view" else "Navigate",
                        callback_data="maps_noop",
                    )
                ]
            )
            rows.extend(_link_rows(action_links))
    else:
        rows.extend(_link_rows(links))

    if all_links is not None and location is not None and len(all_links) > len(links):
        rows.append(
            [
                InlineKeyboardButton(
                    text=all_maps_text,
                    callback_data=(
                        "maps_all:"
                        f"{location.latitude:.7f}:"
                        f"{location.longitude:.7f}"
                    ),
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _link_rows(links: list[MapLink]) -> list[list[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton(text=link.title, url=link.url)
            for link in links[index : index + 2]
        ]
        for index in range(0, len(links), 2)
    ]
