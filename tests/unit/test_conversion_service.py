import pytest

from app.core.location import Location
from app.providers.base import MapProvider
from app.services.conversion import LocationConverter, UnsupportedInputError


class StaticProvider(MapProvider):
    name = "static"
    title = "Static Maps"
    supports_export = True

    def build_url(self, location: Location) -> str:
        return f"https://example.test/{location.latitude},{location.longitude}"


@pytest.mark.asyncio
async def test_location_converter_parses_decimal_coordinates() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse("Отель - 42.4439296, 42.3915008")

    assert location.latitude == 42.4439296
    assert location.longitude == 42.3915008


@pytest.mark.asyncio
async def test_location_converter_parses_google_maps_url_before_decimal_coordinates() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://www.google.com/maps/@41.6935000,44.8015790,17z"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579
    assert location.source == "google_maps_url"


@pytest.mark.asyncio
async def test_location_converter_parses_yandex_maps_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://yandex.com/maps/?ll=44.8015790%2C41.6935000&z=17"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579
    assert location.source == "yandex_maps_url"


@pytest.mark.asyncio
async def test_location_converter_parses_apple_maps_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://maps.apple.com/?ll=41.6935000%2C44.8015790"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579
    assert location.source == "apple_maps_url"


@pytest.mark.asyncio
async def test_location_converter_parses_twogis_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse("https://2gis.com/geo/42.3914689,42.4439724")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "twogis_url"


@pytest.mark.asyncio
async def test_location_converter_parses_osm_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://www.openstreetmap.org/?mlat=42.4439724&mlon=42.3914689"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "osm_url"


@pytest.mark.asyncio
async def test_location_converter_parses_waze_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://waze.com/ul?ll=42.4439724%2C42.3914689&navigate=yes"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "waze_url"


@pytest.mark.asyncio
async def test_location_converter_parses_organic_maps_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://omaps.app/map?v=1&ll=42.4439724%2C42.3914689"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "organic_maps_url"


@pytest.mark.asyncio
async def test_location_converter_parses_mapsme_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse(
        "https://dlink.maps.me/map?v=1&ll=42.4439724%2C42.3914689"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "mapsme_url"


@pytest.mark.asyncio
async def test_location_converter_parses_here_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse("https://share.here.com/l/42.4439724,42.3914689")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "here_url"


@pytest.mark.asyncio
async def test_location_converter_parses_osmand_url() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse("https://osmand.net/map/?pin=42.4439724,42.3914689")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "osmand_url"


@pytest.mark.asyncio
async def test_location_converter_parses_full_plus_code() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    location = await converter.parse("8HH4C9VR+MC")

    assert location.latitude == 41.4441875
    assert location.longitude == 42.391062500000004
    assert location.source == "plus_code"


def test_location_converter_builds_links_from_providers() -> None:
    converter = LocationConverter(providers=[StaticProvider()])
    location = Location(latitude=42.4439296, longitude=42.3915008)

    links = converter.get_links(location)

    assert len(links) == 1
    assert links[0].provider == "static"
    assert links[0].title == "Static Maps"
    assert links[0].url == "https://example.test/42.4439296,42.3915008"


def test_location_converter_filters_links_by_action() -> None:
    converter = LocationConverter()
    location = Location(latitude=42.4439296, longitude=42.3915008)

    view_links = converter.get_links(location, action="view")
    navigate_links = converter.get_links(location, action="navigate")

    assert "Yandex Maps" in [link.title for link in view_links]
    assert "Yandex Navigator" not in [link.title for link in view_links]
    assert "Yandex Navigator" in [link.title for link in navigate_links]
    assert all(link.action == "navigate" for link in navigate_links)


@pytest.mark.asyncio
async def test_location_converter_raises_unsupported_input_for_unknown_text() -> None:
    converter = LocationConverter(providers=[StaticProvider()])

    with pytest.raises(UnsupportedInputError):
        await converter.parse("hello world")
