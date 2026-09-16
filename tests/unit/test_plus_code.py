import pytest

from app.core.location import Location
from app.parsers.plus_code import PlusCodeParseError, PlusCodeParser, parse_plus_code
from app.services.geocoding import GeocodingError


class FakeGeocoder:
    async def search(self, query: str) -> Location:
        if query == "Didi Inchkhuri":
            return Location(latitude=42.4435, longitude=42.3915, source="fake_geocoder")

        raise GeocodingError("place was not found")


@pytest.mark.asyncio
async def test_parse_full_plus_code() -> None:
    location = await parse_plus_code("8HH4C9VR+MC")

    assert location.source == "plus_code"
    assert location.latitude == 41.4441875
    assert location.longitude == 42.391062500000004


@pytest.mark.asyncio
async def test_parse_full_plus_code_inside_text() -> None:
    location = await PlusCodeParser().parse("Hotel near 8HH4C9VR+MC in Georgia")

    assert location.latitude == 41.4441875
    assert location.longitude == 42.391062500000004


@pytest.mark.parametrize(
    "value",
    [
        "hello world",
        "INVALID+CODE",
        "C9VR+MC",
    ],
)
@pytest.mark.asyncio
async def test_parse_plus_code_rejects_invalid_or_short_codes(value: str) -> None:
    with pytest.raises(PlusCodeParseError):
        await PlusCodeParser().parse(value)


@pytest.mark.asyncio
async def test_parse_short_plus_code_with_locality() -> None:
    location = await PlusCodeParser(geocoder=FakeGeocoder()).parse(
        "C9VR+MC Didi Inchkhuri"
    )

    assert location.source == "plus_code"
    assert location.address == "Didi Inchkhuri"
    assert location.latitude == 42.4441875
    assert location.longitude == 42.391062500000004


@pytest.mark.asyncio
async def test_parse_short_plus_code_rejects_unknown_locality() -> None:
    with pytest.raises(PlusCodeParseError, match="place was not found"):
        await PlusCodeParser(geocoder=FakeGeocoder()).parse(
            "C9VR+MC completely-nonexistent-place-xyz"
        )
