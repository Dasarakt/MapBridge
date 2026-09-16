from urllib.parse import parse_qs, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class MapsMeUrlParseError(MapBridgeError, ValueError):
    """Raised when a MAPS.ME URL does not contain parseable coordinates."""


_MAPSME_HOSTS = {"dlink.maps.me", "maps.me", "www.maps.me"}


class MapsMeUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _MAPSME_HOSTS:
            raise MapsMeUrlParseError("not a supported MAPS.ME URL")

        query = parse_qs(parsed_url.query)
        for field in ("ll", "cll", "dll", "sll"):
            for candidate in query.get(field, []):
                location = self._parse_lat_lon(candidate)
                if location is not None:
                    return location

        raise MapsMeUrlParseError("MAPS.ME URL does not contain coordinates")

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="mapsme_url",
        )


async def parse_mapsme_url(value: str) -> Location:
    return await MapsMeUrlParser().parse(value)

