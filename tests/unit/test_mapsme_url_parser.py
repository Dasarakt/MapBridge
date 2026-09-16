import json
from pathlib import Path

import pytest

from app.parsers.mapsme_url import MapsMeUrlParseError, MapsMeUrlParser, parse_mapsme_url


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def mapsme_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "mapsme"]


@pytest.mark.parametrize("fixture", mapsme_fixtures())
@pytest.mark.asyncio
async def test_mapsme_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await MapsMeUrlParser().parse(str(fixture["input"]))

    assert location.source == "mapsme_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_mapsme_url_extracts_ll_coordinates() -> None:
    location = await parse_mapsme_url(
        "https://dlink.maps.me/map?v=1&ll=42.4439724%2C42.3914689"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_mapsme_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(MapsMeUrlParseError):
        await MapsMeUrlParser().parse("https://dlink.maps.me/search?query=food")


@pytest.mark.asyncio
async def test_mapsme_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(MapsMeUrlParseError):
        await MapsMeUrlParser().parse(
            "https://example.com/map?v=1&ll=42.4439724,42.3914689"
        )

