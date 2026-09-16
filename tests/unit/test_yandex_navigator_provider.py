from app.core.location import Location
from app.providers.yandex_navigator import YandexNavigatorProvider


def test_yandex_navigator_provider_builds_point_url() -> None:
    provider = YandexNavigatorProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "yandexnavi://show_point_on_map?lat=42.4439724&lon=42.3914689"
    )


def test_yandex_navigator_provider_builds_route_url() -> None:
    provider = YandexNavigatorProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_navigation_url(location)
        == "yandexnavi://build_route_on_map?lat_to=42.4439724&lon_to=42.3914689"
    )


def test_yandex_navigator_provider_preserves_negative_coordinates() -> None:
    provider = YandexNavigatorProvider()
    location = Location(latitude=-33.8569, longitude=151.2152)

    assert (
        provider.build_navigation_url(location)
        == "yandexnavi://build_route_on_map?lat_to=-33.8569000&lon_to=151.2152000"
    )


def test_yandex_navigator_provider_builds_navigation_link() -> None:
    provider = YandexNavigatorProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location, action="navigate")

    assert link.provider == "yandex_navigator"
    assert link.title == "Yandex Navigator"
    assert link.action == "navigate"
    assert (
        link.url
        == "https://yandex.ru/navi/?whatshere%5Bpoint%5D=42.3914689%2C42.4439724&whatshere%5Bzoom%5D=17&lang=ru&from=navi"
    )


def test_yandex_navigator_provider_keeps_deep_link_separate_from_telegram_url() -> None:
    provider = YandexNavigatorProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_navigation_url(location)
        == "yandexnavi://build_route_on_map?lat_to=42.4439724&lon_to=42.3914689"
    )
    assert provider.build_link(location, action="navigate").url.startswith(
        "https://yandex.ru/navi/?"
    )
