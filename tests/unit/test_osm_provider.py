from app.core.location import Location
from app.providers.osm import OpenStreetMapProvider


def test_openstreetmap_provider_builds_coordinate_url() -> None:
    provider = OpenStreetMapProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert (
        provider.build_url(location)
        == "https://www.openstreetmap.org/?mlat=42.4439724&mlon=42.3914689#map=17/42.4439724/42.3914689"
    )


def test_openstreetmap_provider_uses_location_zoom_when_available() -> None:
    provider = OpenStreetMapProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689, zoom=15)

    assert provider.build_url(location).endswith("#map=15/42.4439724/42.3914689")


def test_openstreetmap_provider_builds_map_link() -> None:
    provider = OpenStreetMapProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "osm"
    assert link.title == "OpenStreetMap"
    assert (
        link.url
        == "https://www.openstreetmap.org/?mlat=42.4439724&mlon=42.3914689#map=17/42.4439724/42.3914689"
    )

