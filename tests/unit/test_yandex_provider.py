from app.core.location import Location
from app.providers.yandex import YandexMapsProvider


def test_yandex_maps_provider_builds_coordinate_url() -> None:
    provider = YandexMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://yandex.com/maps/?ll=42.3914689%2C42.4439724&pt=42.3914689%2C42.4439724&z=17"
    )


def test_yandex_maps_provider_uses_location_zoom_when_available() -> None:
    provider = YandexMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689, zoom=15)

    assert provider.build_url(location).endswith("&z=15")


def test_yandex_maps_provider_builds_map_link() -> None:
    provider = YandexMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "yandex"
    assert link.title == "Yandex Maps"
    assert (
        link.url
        == "https://yandex.com/maps/?ll=42.3914689%2C42.4439724&pt=42.3914689%2C42.4439724&z=17"
    )

