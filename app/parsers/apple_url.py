from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class AppleMapsUrlParseError(MapBridgeError, ValueError):
    """Raised when an Apple Maps URL does not contain parseable coordinates."""


_APPLE_MAPS_HOSTS = {"maps.apple.com"}
_COORDINATE_QUERY_FIELDS = (
    "ll",
    "sll",
    "near",
    "coordinate",
    "center",
    "q",
    "daddr",
)


class AppleMapsUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _APPLE_MAPS_HOSTS:
            raise AppleMapsUrlParseError("not a supported Apple Maps URL")

        query = parse_qs(parsed_url.query)
        for field in _COORDINATE_QUERY_FIELDS:
            for candidate in query.get(field, []):
                location = self._parse_lat_lon(candidate)
                if location is not None:
                    return location

        raise AppleMapsUrlParseError("Apple Maps URL does not contain coordinates")

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(unquote(value))
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="apple_maps_url",
        )


async def parse_apple_maps_url(value: str) -> Location:
    return await AppleMapsUrlParser().parse(value)

