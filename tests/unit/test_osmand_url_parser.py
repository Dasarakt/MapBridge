import json
from pathlib import Path

import pytest

from app.parsers.osmand_url import OsmAndUrlParseError, OsmAndUrlParser, parse_osmand_url


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def osmand_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "osmand"]


@pytest.mark.parametrize("fixture", osmand_fixtures())
@pytest.mark.asyncio
async def test_osmand_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await OsmAndUrlParser().parse(str(fixture["input"]))

    assert location.source == "osmand_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_osmand_url_extracts_pin_coordinates() -> None:
    location = await parse_osmand_url("https://osmand.net/map/?pin=42.4439724,42.3914689")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_osmand_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(OsmAndUrlParseError):
        await OsmAndUrlParser().parse("https://osmand.net/map/search")


@pytest.mark.asyncio
async def test_osmand_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(OsmAndUrlParseError):
        await OsmAndUrlParser().parse("https://example.com/map/?pin=42.4439724,42.3914689")

