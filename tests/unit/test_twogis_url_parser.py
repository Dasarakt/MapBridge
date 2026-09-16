import json
from pathlib import Path

import pytest

from app.parsers.twogis_url import (
    TwoGisUrlParseError,
    TwoGisUrlParser,
    parse_twogis_url,
)


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def twogis_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "twogis"]


@pytest.mark.parametrize("fixture", twogis_fixtures())
@pytest.mark.asyncio
async def test_twogis_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await TwoGisUrlParser().parse(str(fixture["input"]))

    assert location.source == "twogis_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_twogis_url_extracts_geo_coordinates() -> None:
    location = await parse_twogis_url("https://2gis.com/geo/42.3914689,42.4439724")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_twogis_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(TwoGisUrlParseError):
        await TwoGisUrlParser().parse("https://2gis.ru/firm/70000001063199639")


@pytest.mark.asyncio
async def test_twogis_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(TwoGisUrlParseError):
        await TwoGisUrlParser().parse("https://example.com/geo/42.3914689,42.4439724")

