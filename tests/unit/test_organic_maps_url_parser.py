import json
from pathlib import Path

import pytest

from app.parsers.organic_maps_url import (
    OrganicMapsUrlParseError,
    OrganicMapsUrlParser,
    parse_organic_maps_url,
)


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def organic_maps_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "organic_maps"]


@pytest.mark.parametrize("fixture", organic_maps_fixtures())
@pytest.mark.asyncio
async def test_organic_maps_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await OrganicMapsUrlParser().parse(str(fixture["input"]))

    assert location.source == "organic_maps_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_organic_maps_url_extracts_ll_coordinates() -> None:
    location = await parse_organic_maps_url(
        "https://omaps.app/map?v=1&ll=42.4439724%2C42.3914689"
    )

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689


@pytest.mark.asyncio
async def test_organic_maps_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(OrganicMapsUrlParseError):
        await OrganicMapsUrlParser().parse("https://omaps.app/map?v=1&n=hotel")


@pytest.mark.asyncio
async def test_organic_maps_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(OrganicMapsUrlParseError):
        await OrganicMapsUrlParser().parse(
            "https://example.com/map?v=1&ll=42.4439724,42.3914689"
        )

