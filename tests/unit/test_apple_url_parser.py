import json
from pathlib import Path

import pytest

from app.parsers.apple_url import (
    AppleMapsUrlParseError,
    AppleMapsUrlParser,
    parse_apple_maps_url,
)


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def apple_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "apple"]


@pytest.mark.parametrize("fixture", apple_fixtures())
@pytest.mark.asyncio
async def test_apple_maps_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await AppleMapsUrlParser().parse(str(fixture["input"]))

    assert location.source == "apple_maps_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_apple_maps_url_extracts_ll_coordinates() -> None:
    location = await parse_apple_maps_url(
        "https://maps.apple.com/?ll=41.6935000%2C44.8015790"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579


@pytest.mark.asyncio
async def test_apple_maps_url_parser_extracts_daddr_coordinates() -> None:
    location = await AppleMapsUrlParser().parse(
        "https://maps.apple.com/?daddr=42.4439724%2C42.3914689&dirflg=d"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_apple_maps_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(AppleMapsUrlParseError):
        await AppleMapsUrlParser().parse("https://maps.apple.com/?q=Tbilisi")


@pytest.mark.asyncio
async def test_apple_maps_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(AppleMapsUrlParseError):
        await AppleMapsUrlParser().parse(
            "https://example.com/?ll=41.6935000%2C44.8015790"
        )

