from urllib.parse import parse_qs, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class WazeUrlParseError(MapBridgeError, ValueError):
    """Raised when a Waze URL does not contain parseable coordinates."""


_WAZE_HOSTS = {
    "waze.com",
    "www.waze.com",
}


class WazeUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _WAZE_HOSTS:
            raise WazeUrlParseError("not a supported Waze URL")

        query = parse_qs(parsed_url.query)
        for candidate in query.get("ll", []):
            location = self._parse_lat_lon(candidate)
            if location is not None:
                return location

        raise WazeUrlParseError("Waze URL does not contain coordinates")

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="waze_url",
        )


async def parse_waze_url(value: str) -> Location:
    return await WazeUrlParser().parse(value)

