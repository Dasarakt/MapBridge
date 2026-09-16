import re
from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import InvalidLocationError, Location
from app.core.resolver import RedirectResolutionError, RedirectResolver
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates
from app.parsers.plus_code import PlusCodeParseError, PlusCodeParser
from app.services.geocoding import Geocoder, GeocodingError, create_default_geocoder


class GoogleMapsUrlParseError(MapBridgeError, ValueError):
    """Raised when a Google Maps URL does not contain parseable coordinates."""


_GOOGLE_MAPS_HOSTS = {
    "google.com",
    "www.google.com",
    "maps.google.com",
}
_GOOGLE_SHORT_LINK_HOSTS = {"maps.app.goo.gl", "share.google"}
_COORDINATE_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
_PATH_COORDINATES_PATTERN = re.compile(
    rf"@(?P<latitude>{_COORDINATE_NUMBER}),(?P<longitude>{_COORDINATE_NUMBER})"
)
_BANG_COORDINATES_PATTERN = re.compile(
    rf"!3d(?P<latitude>{_COORDINATE_NUMBER})!4d(?P<longitude>{_COORDINATE_NUMBER})"
)
_PLACE_PATH_PATTERN = re.compile(r"/maps/place/(?P<place>[^/]+)")
_PLUS_CODE_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?P<code>[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3})(?![A-Z0-9])",
    re.IGNORECASE,
)
_QUERY_FIELDS = ("q", "query", "ll", "center", "destination")
_SEARCH_QUERY_ALIASES = {
    "Kutaisi Cable Car Bottom Station": "ქუთაისის საბაგირო",
}


class GoogleMapsUrlParser(LocationParser):
    def __init__(
        self,
        redirect_resolver: RedirectResolver | None = None,
        plus_code_parser: PlusCodeParser | None = None,
        geocoder: Geocoder | None = None,
    ) -> None:
        self._redirect_resolver = redirect_resolver or RedirectResolver()
        self._plus_code_parser = plus_code_parser or PlusCodeParser()
        self._geocoder = geocoder or create_default_geocoder()

    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host in _GOOGLE_SHORT_LINK_HOSTS:
            return await self._parse_short_url(value)

        if host not in _GOOGLE_MAPS_HOSTS:
            raise GoogleMapsUrlParseError("not a supported Google Maps URL")

        if parsed_url.path == "/search":
            return await self._parse_search_url(parsed_url)

        if "/maps" not in parsed_url.path and host != "maps.google.com":
            raise GoogleMapsUrlParseError("not a Google Maps location URL")

        return await self._parse_url(parsed_url)

    async def _parse_short_url(self, value: str) -> Location:
        try:
            final_url = await self._redirect_resolver.resolve(value)
        except RedirectResolutionError as exc:
            raise GoogleMapsUrlParseError(str(exc)) from exc

        location = await GoogleMapsUrlParser(
            redirect_resolver=self._redirect_resolver,
            plus_code_parser=self._plus_code_parser,
            geocoder=self._geocoder,
        ).parse(final_url)
        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            name=location.name,
            address=location.address,
            zoom=location.zoom,
            source="google_maps_short_url",
        )

    async def _parse_url(self, parsed_url) -> Location:
        url_parts = [
            unquote(parsed_url.path),
            unquote(parsed_url.query),
            unquote(parsed_url.fragment),
        ]

        for part in url_parts:
            location = self._parse_known_coordinate_pattern(part)
            if location is not None:
                return location

        query = parse_qs(parsed_url.query)
        for field in _QUERY_FIELDS:
            for candidate in query.get(field, []):
                location = self._parse_coordinate_text(candidate)
                if location is not None:
                    return location

        location = await self._parse_plus_code_from_place_path(parsed_url.path)
        if location is not None:
            return location

        raise GoogleMapsUrlParseError("Google Maps URL does not contain coordinates")

    def _parse_known_coordinate_pattern(self, value: str) -> Location | None:
        for pattern in (_PATH_COORDINATES_PATTERN, _BANG_COORDINATES_PATTERN):
            match = pattern.search(value)
            if match is None:
                continue

            try:
                return Location(
                    latitude=float(match.group("latitude")),
                    longitude=float(match.group("longitude")),
                    source="google_maps_url",
                )
            except InvalidLocationError as exc:
                raise GoogleMapsUrlParseError(str(exc)) from exc

        return None

    def _parse_coordinate_text(self, value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="google_maps_url",
        )

    async def _parse_plus_code_from_place_path(self, path: str) -> Location | None:
        match = _PLACE_PATH_PATTERN.search(unquote(path))
        if match is None:
            return None

        place = match.group("place")
        plus_code_match = _PLUS_CODE_PATTERN.search(place)
        if plus_code_match is None:
            return None

        code = plus_code_match.group("code").upper()
        locality = place[plus_code_match.end() :].replace("+", " ")
        if "," in locality:
            locality = locality.rsplit(",", maxsplit=1)[-1]
        locality = " ".join(locality.split())

        try:
            return await self._plus_code_parser.parse(f"{code} {locality}")
        except PlusCodeParseError as exc:
            raise GoogleMapsUrlParseError(str(exc)) from exc

    async def _parse_search_url(self, parsed_url) -> Location:
        query = parse_qs(parsed_url.query)
        if not self._is_location_search(query):
            raise GoogleMapsUrlParseError("not a Google location search URL")

        search_query = next(iter(query.get("q", [])), "").strip()
        if not search_query:
            raise GoogleMapsUrlParseError("Google location search URL has no query")

        location = await self._geocode_search_query(search_query)

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            name=search_query,
            address=location.address,
            zoom=location.zoom,
            source="google_maps_search_url",
        )

    def _is_location_search(self, query: dict[str, list[str]]) -> bool:
        sources = query.get("source", [])
        return "kgmid" in query or any(
            source.startswith("sh/x/loc/") for source in sources
        )

    async def _geocode_search_query(self, search_query: str) -> Location:
        queries = [search_query]
        alias = _SEARCH_QUERY_ALIASES.get(search_query)
        if alias is not None:
            queries.append(alias)

        last_error: GeocodingError | None = None
        for query in queries:
            try:
                return await self._geocoder.search(query)
            except GeocodingError as exc:
                last_error = exc

        raise GoogleMapsUrlParseError(str(last_error or "place was not found"))


async def parse_google_maps_url(value: str) -> Location:
    return await GoogleMapsUrlParser().parse(value)
