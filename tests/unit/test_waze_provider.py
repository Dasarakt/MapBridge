from app.core.location import Location
from app.providers.waze import WazeProvider


def test_waze_provider_builds_coordinate_url() -> None:
    provider = WazeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://waze.com/ul?ll=42.4439724%2C42.3914689&zoom=17"
    )


def test_waze_provider_uses_location_zoom_when_available() -> None:
    provider = WazeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689, zoom=15)

    assert provider.build_url(location).endswith("&zoom=15")


def test_waze_provider_builds_map_link() -> None:
    provider = WazeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "waze"
    assert link.title == "Waze"
    assert link.action == "view"
    assert link.url == "https://waze.com/ul?ll=42.4439724%2C42.3914689&zoom=17"


def test_waze_provider_builds_navigation_link() -> None:
    provider = WazeProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location, action="navigate")

    assert link.provider == "waze"
    assert link.title == "Waze"
    assert link.action == "navigate"
    assert (
        link.url
        == "https://waze.com/ul?ll=42.4439724%2C42.3914689&navigate=yes&zoom=17"
    )
