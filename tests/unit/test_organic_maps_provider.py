from app.core.location import Location
from app.providers.organic_maps import OrganicMapsProvider


def test_organic_maps_provider_builds_coordinate_url() -> None:
    provider = OrganicMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://omaps.app/map?v=1&ll=42.4439724%2C42.3914689"
    )


def test_organic_maps_provider_includes_location_name_when_available() -> None:
    provider = OrganicMapsProvider()
    location = Location(
        latitude=42.4439724,
        longitude=42.3914689,
        name="hotel pillows",
    )

    assert (
        provider.build_url(location)
        == "https://omaps.app/map?v=1&ll=42.4439724%2C42.3914689&n=hotel+pillows"
    )


def test_organic_maps_provider_builds_map_link() -> None:
    provider = OrganicMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "organic_maps"
    assert link.title == "Organic Maps"
    assert link.url == "https://omaps.app/map?v=1&ll=42.4439724%2C42.3914689"

