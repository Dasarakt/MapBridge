from app.core.location import Location
from app.providers.mapsme import MapsMeProvider


def test_mapsme_provider_builds_coordinate_url() -> None:
    provider = MapsMeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://dlink.maps.me/map?v=1&ll=42.4439724%2C42.3914689"
    )


def test_mapsme_provider_includes_location_name_when_available() -> None:
    provider = MapsMeProvider()
    location = Location(
        latitude=42.4439724,
        longitude=42.3914689,
        name="hotel pillows",
    )

    assert (
        provider.build_url(location)
        == "https://dlink.maps.me/map?v=1&ll=42.4439724%2C42.3914689&n=hotel+pillows"
    )


def test_mapsme_provider_builds_map_link() -> None:
    provider = MapsMeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "mapsme"
    assert link.title == "MAPS.ME"
    assert link.url == "https://dlink.maps.me/map?v=1&ll=42.4439724%2C42.3914689"

