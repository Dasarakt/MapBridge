import json
from pathlib import Path

import pytest

from app.parsers.yandex_url import (
    YandexMapsUrlParseError,
    YandexMapsUrlParser,
    parse_yandex_maps_url,
)


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "map_urls.json"


def yandex_fixtures() -> list[dict[str, object]]:
    fixtures = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return [fixture for fixture in fixtures if fixture["provider"] == "yandex"]


@pytest.mark.parametrize("fixture", yandex_fixtures())
@pytest.mark.asyncio
async def test_yandex_maps_url_parser_extracts_fixture_coordinates(
    fixture: dict[str, object],
) -> None:
    location = await YandexMapsUrlParser().parse(str(fixture["input"]))

    assert location.source == "yandex_maps_url"
    assert location.latitude == fixture["latitude"]
    assert location.longitude == fixture["longitude"]


@pytest.mark.asyncio
async def test_parse_yandex_maps_url_extracts_ll_coordinates() -> None:
    location = await parse_yandex_maps_url(
        "https://yandex.com/maps/?ll=44.8015790%2C41.6935000&z=17"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579


@pytest.mark.asyncio
async def test_yandex_maps_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(YandexMapsUrlParseError):
        await YandexMapsUrlParser().parse("https://yandex.com/maps/10277/tbilisi/")


@pytest.mark.asyncio
async def test_yandex_maps_url_parser_rejects_unknown_host() -> None:
    with pytest.raises(YandexMapsUrlParseError):
        await YandexMapsUrlParser().parse(
            "https://example.com/maps/?ll=44.8015790%2C41.6935000"
        )

