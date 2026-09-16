import json
from pathlib import Path

import pytest

from app.parsers.here_url import HereUrlParseError, HereUrlParser, parse_here_url


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def here_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "here"]


@pytest.mark.parametrize("fixture", here_fixtures())
@pytest.mark.asyncio
async def test_here_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await HereUrlParser().parse(str(fixture["input"]))

    assert location.source == "here_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_here_url_extracts_share_location_coordinates() -> None:
    location = await parse_here_url("https://share.here.com/l/42.4439724,42.3914689")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_here_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(HereUrlParseError):
        await HereUrlParser().parse("https://wego.here.com/")


@pytest.mark.asyncio
async def test_here_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(HereUrlParseError):
        await HereUrlParser().parse("https://example.com/l/42.4439724,42.3914689")

