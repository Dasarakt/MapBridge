from app.bot.keyboards.maps import build_map_links_keyboard
from app.core.location import Location
from app.providers.base import MapLink


def test_build_map_links_keyboard_groups_buttons_by_pairs() -> None:
    keyboard = build_map_links_keyboard(
        [
            MapLink(provider="a", title="A", url="https://a.example"),
            MapLink(provider="b", title="B", url="https://b.example"),
            MapLink(provider="c", title="C", url="https://c.example"),
        ]
    )

    assert len(keyboard.inline_keyboard) == 2
    assert [button.text for button in keyboard.inline_keyboard[0]] == ["A", "B"]
    assert [button.text for button in keyboard.inline_keyboard[1]] == ["C"]


def test_build_map_links_keyboard_groups_view_and_navigation_links() -> None:
    keyboard = build_map_links_keyboard(
        [
            MapLink(provider="google", title="Google Maps", url="https://g.example"),
            MapLink(
                provider="yandex_navigator",
                title="Yandex Navigator",
                url="yandexnavi://build_route_on_map?lat_to=1&lon_to=2",
                action="navigate",
            ),
            MapLink(
                provider="waze",
                title="Waze",
                url="https://w.example",
                action="navigate",
            ),
        ]
    )

    assert [button.text for button in keyboard.inline_keyboard[0]] == ["View"]
    assert [button.text for button in keyboard.inline_keyboard[1]] == ["Google Maps"]
    assert [button.text for button in keyboard.inline_keyboard[2]] == ["Navigate"]
    assert [button.text for button in keyboard.inline_keyboard[3]] == [
        "Yandex Navigator",
        "Waze",
    ]


def test_build_map_links_keyboard_adds_all_maps_callback_when_links_are_hidden() -> None:
    keyboard = build_map_links_keyboard(
        [MapLink(provider="a", title="A", url="https://a.example")],
        all_links=[
            MapLink(provider="a", title="A", url="https://a.example"),
            MapLink(provider="b", title="B", url="https://b.example"),
        ],
        location=Location(latitude=42.4439724, longitude=42.3914689),
        all_maps_text="All maps",
    )

    all_maps_button = keyboard.inline_keyboard[-1][0]
    assert all_maps_button.text == "All maps"
    assert all_maps_button.callback_data == "maps_all:42.4439724:42.3914689"
