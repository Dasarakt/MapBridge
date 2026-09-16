from urllib.parse import parse_qs, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class OrganicMapsUrlParseError(MapBridgeError, ValueError):
    """Raised when an Organic Maps URL does not contain parseable coordinates."""


_ORGANIC_MAPS_HOSTS = {"omaps.app", "www.omaps.app"}


class OrganicMapsUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _ORGANIC_MAPS_HOSTS:
            raise OrganicMapsUrlParseError("not a supported Organic Maps URL")

        query = parse_qs(parsed_url.query)
        for candidate in query.get("ll", []):
            location = self._parse_lat_lon(candidate)
            if location is not None:
                return location

        raise OrganicMapsUrlParseError("Organic Maps URL does not contain coordinates")

    @staticmethod
    def _parse_lat_lon(value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return Location(
            latitude=location.latitude,
            longitude=location.longitude,
            source="organic_maps_url",
        )


async def parse_organic_maps_url(value: str) -> Location:
    return await OrganicMapsUrlParser().parse(value)

