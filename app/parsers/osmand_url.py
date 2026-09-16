from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class OsmAndUrlParseError(MapBridgeError, ValueError):
    """Raised when an OsmAnd URL does not contain parseable coordinates."""


_OSMAND_HOSTS = {"osmand.net", "www.osmand.net"}


class OsmAndUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _OSMAND_HOSTS:
            raise OsmAndUrlParseError("not a supported OsmAnd URL")

        query = parse_qs(parsed_url.query)
        for field in ("pin", "finish", "start"):
            for candidate in query.get(field, []):
                location = self._parse_lat_lon(candidate)
                if location is not None:
                    return location

        location = self._parse_hash_coordinates(parsed_url.fragment)
        if location is not None:
            return location

        raise OsmAndUrlParseError("OsmAnd URL does not contain coordinates")

    def _parse_hash_coordinates(self, fragment: str) -> Location | None:
        parts = unquote(fragment).split("/")
        if len(parts) < 3:
            return None

        return self._parse_lat_lon(",".join(parts[1:3]))

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="osmand_url",
        )


async def parse_osmand_url(value: str) -> Location:
    return await OsmAndUrlParser().parse(value)

