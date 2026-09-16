from app.core.location import Location
from app.providers.apple import AppleMapsProvider


def test_apple_maps_provider_builds_coordinate_url() -> None:
    provider = AppleMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://maps.apple.com/?ll=42.4439724%2C42.3914689&q=42.4439724%2C42.3914689"
    )


def test_apple_maps_provider_builds_map_link() -> None:
    provider = AppleMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "apple"
    assert link.title == "Apple Maps"
    assert (
        link.url
        == "https://maps.apple.com/?ll=42.4439724%2C42.3914689&q=42.4439724%2C42.3914689"
    )

