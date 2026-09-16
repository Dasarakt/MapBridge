from app.core.location import Location
from app.providers.twogis import TwoGisProvider


def test_twogis_provider_builds_coordinate_url() -> None:
    provider = TwoGisProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert provider.build_url(location) == "https://2gis.com/geo/42.3914689,42.4439724"


def test_twogis_provider_builds_map_link() -> None:
    provider = TwoGisProvider()
    location = Location(latitude=42.4439724, longitude=42.3914689)

    link = provider.build_link(location)

    assert link.provider == "twogis"
    assert link.title == "2GIS"
    assert link.url == "https://2gis.com/geo/42.3914689,42.4439724"

