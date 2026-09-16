from app.core.location import Location
from app.providers.google import GoogleMapsProvider


def test_google_maps_provider_builds_coordinate_url() -> None:
    provider = GoogleMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://www.google.com/maps/search/?api=1&query=42.4439724%2C42.3914689"
    )


def test_google_maps_provider_builds_map_link() -> None:
    provider = GoogleMapsProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "google"
    assert link.title == "Google Maps"
    assert (
        link.url
        == "https://www.google.com/maps/search/?api=1&query=42.4439724%2C42.3914689"
    )

