from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class HereUrlParseError(MapBridgeError, ValueError):
    """Raised when a HERE URL does not contain parseable coordinates."""


_HERE_HOSTS = {
    "share.here.com",
    "wego.here.com",
    "www.here.com",
}


class HereUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _HERE_HOSTS:
            raise HereUrlParseError("not a supported HERE URL")

        if host == "share.here.com":
            location = self._parse_share_path(parsed_url.path)
            if location is not None:
                return location

        query = parse_qs(parsed_url.query)
        for candidate in query.get("map", []):
            location = self._parse_map_parameter(candidate)
            if location is not None:
                return location

        raise HereUrlParseError("HERE URL does not contain coordinates")

    def _parse_share_path(self, path: str) -> Location | None:
        parts = unquote(path).strip("/").split("/")
        if len(parts) < 2 or parts[0] != "l":
            return None

        return self._parse_lat_lon(",".join(parts[1].split(",")[:2]))

    def _parse_map_parameter(self, value: str) -> Location | None:
        parts = unquote(value).split(",")
        if len(parts) < 2:
            return None

        return self._parse_lat_lon(",".join(parts[:2]))

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="here_url",
        )


async def parse_here_url(value: str) -> Location:
    return await HereUrlParser().parse(value)

