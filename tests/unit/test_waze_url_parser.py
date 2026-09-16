import json
from pathlib import Path

import pytest

from app.parsers.waze_url import WazeUrlParseError, WazeUrlParser, parse_waze_url


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def waze_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "waze"]


@pytest.mark.parametrize("fixture", waze_fixtures())
@pytest.mark.asyncio
async def test_waze_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await WazeUrlParser().parse(str(fixture["input"]))

    assert location.source == "waze_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_waze_url_extracts_ll_coordinates() -> None:
    location = await parse_waze_url(
        "https://waze.com/ul?ll=42.4439724%2C42.3914689&navigate=yes"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_waze_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(WazeUrlParseError):
        await WazeUrlParser().parse("https://waze.com/ul?q=Tbilisi")


@pytest.mark.asyncio
async def test_waze_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(WazeUrlParseError):
        await WazeUrlParser().parse("https://example.com/ul?ll=42.4439724,42.3914689")

