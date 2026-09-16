import pytest

from app.core.location import Location
from app.parsers.google_url import (
    GoogleMapsUrlParseError,
    GoogleMapsUrlParser,
    parse_google_maps_url,
)


class FakeRedirectResolver:
    def __init__(self, expected_url: str, final_url: str | None = None) -> None:
        self.expected_url = expected_url
        self.final_url = final_url or "https://www.google.com/maps/@42.4439724,42.3914689,17z"

    async def resolve(self, value: str) -> str:
        assert value == self.expected_url
        return self.final_url


class FakePlusCodeParser:
    def __init__(self) -> None:
        self.values: list[str] = []

    async def parse(self, value: str) -> Location:
        self.values.append(value)
        return Location(latitude=41.634088, longitude=41.612784, source="plus_code")


class FakeGeocoder:
    def __init__(self, fail_first_query: bool = True) -> None:
        self.queries: list[str] = []
        self.fail_first_query = fail_first_query

    async def search(self, query: str) -> Location:
        self.queries.append(query)
        if self.fail_first_query and query == "Kutaisi Cable Car Bottom Station":
            from app.services.geocoding import GeocodingError

            raise GeocodingError("place was not found")
        return Location(latitude=41.634088, longitude=41.612784, source="fake")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.google.com/maps/place/Falafel+M.+Sahyoun/@33.8904447,35.5044618,16z",
        "https://www.google.com/maps/@41.6935000,44.8015790,17z",
        "https://maps.google.com/maps?q=55.751809,37.6130029",
        "https://www.google.com/maps/search/?api=1&query=47.5951518%2C-122.3316393",
        "https://www.google.com/maps/dir/?api=1&destination=-33.8569000%2C151.2152000",
        "https://www.google.com/maps/place/Example/data=!3m1!4b1!4m6!3d41.6935000!4d44.8015790",
    ],
)
@pytest.mark.asyncio
async def test_google_maps_url_parser_extracts_coordinates(url: str) -> None:
    location = await GoogleMapsUrlParser().parse(url)

    assert location.source == "google_maps_url"
    assert isinstance(location.latitude, float)
    assert isinstance(location.longitude, float)


@pytest.mark.asyncio
async def test_parse_google_maps_url_extracts_path_coordinates() -> None:
    location = await parse_google_maps_url(
        "https://www.google.com/maps/@41.6935000,44.8015790,17z"
    )

    assert location.latitude == 41.6935
    assert location.longitude == 44.801579


@pytest.mark.asyncio
async def test_google_maps_url_parser_resolves_short_url() -> None:
    location = await GoogleMapsUrlParser(
        redirect_resolver=FakeRedirectResolver(
            "https://maps.app.goo.gl/CzhNt98a8pnGuXiX9"
        )
    ).parse("https://maps.app.goo.gl/CzhNt98a8pnGuXiX9")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "google_maps_short_url"


@pytest.mark.asyncio
async def test_google_maps_url_parser_resolves_share_google_url() -> None:
    location = await GoogleMapsUrlParser(
        redirect_resolver=FakeRedirectResolver(
            "https://share.google/L8GcE065LmBcyavJs"
        )
    ).parse("https://share.google/L8GcE065LmBcyavJs")

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.source == "google_maps_short_url"


@pytest.mark.asyncio
async def test_google_maps_url_parser_resolves_share_google_search_url() -> None:
    geocoder = FakeGeocoder()
    location = await GoogleMapsUrlParser(
        redirect_resolver=FakeRedirectResolver(
            "https://share.google/L8GcE065LmBcyavJs",
            final_url=(
                "https://www.google.com/search?"
                "kgmid=/g/11cs5pcrwb"
                "&q=Kutaisi+Cable+Car+Bottom+Station"
                "&source=sh/x/loc/act/m1/5"
            ),
        ),
        geocoder=geocoder,
    ).parse("https://share.google/L8GcE065LmBcyavJs")

    assert location.latitude == 41.634088
    assert location.longitude == 41.612784
    assert location.name == "Kutaisi Cable Car Bottom Station"
    assert location.source == "google_maps_short_url"
    assert geocoder.queries == [
        "Kutaisi Cable Car Bottom Station",
        "ქუთაისის საბაგირო",
    ]


@pytest.mark.asyncio
async def test_google_maps_url_parser_uses_first_successful_search_geocoder() -> None:
    geocoder = FakeGeocoder(fail_first_query=False)
    location = await GoogleMapsUrlParser(
        redirect_resolver=FakeRedirectResolver(
            "https://share.google/L8GcE065LmBcyavJs",
            final_url=(
                "https://www.google.com/search?"
                "kgmid=/g/example"
                "&q=Any+Google+Place"
                "&source=sh/x/loc/act/m1/5"
            ),
        ),
        geocoder=geocoder,
    ).parse("https://share.google/L8GcE065LmBcyavJs")

    assert location.latitude == 41.634088
    assert location.longitude == 41.612784
    assert location.name == "Any Google Place"
    assert geocoder.queries == ["Any Google Place"]


@pytest.mark.asyncio
async def test_google_maps_url_parser_extracts_plus_code_from_place_path() -> None:
    plus_code_parser = FakePlusCodeParser()
    location = await GoogleMapsUrlParser(plus_code_parser=plus_code_parser).parse(
        "https://www.google.com/maps/place/"
        "C9RR%2BQ9Q+hotel+pillows,+Didi+Inchkhuri/"
        "data=!4m2!3m1!1s0x405c69006d188aa1:0xf3c0e82f673c9640"
    )

    assert location.latitude == 41.634088
    assert location.longitude == 41.612784
    assert plus_code_parser.values == ["C9RR+Q9Q Didi Inchkhuri"]


@pytest.mark.asyncio
async def test_google_maps_url_parser_rejects_url_without_coordinates() -> None:
    with pytest.raises(GoogleMapsUrlParseError):
        await GoogleMapsUrlParser().parse("https://www.google.com/maps/place/Tbilisi")
