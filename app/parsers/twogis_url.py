import re
from urllib.parse import unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import InvalidLocationError, Location
from app.parsers.base import LocationParser


class TwoGisUrlParseError(MapBridgeError, ValueError):
    """Raised when a 2GIS URL does not contain parseable coordinates."""


_TWOGIS_HOST_SUFFIXES = (
    "2gis.com",
    "2gis.ru",
    "2gis.kz",
    "2gis.ae",
)
_COORDINATE_NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
_LON_LAT_PATTERN = re.compile(
    rf"(?P<longitude>{_COORDINATE_NUMBER}),(?P<latitude>{_COORDINATE_NUMBER})"
)


class TwoGisUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host is None or not self._is_twogis_host(host):
            raise TwoGisUrlParseError("not a supported 2GIS URL")

        path = unquote(parsed_url.path)
        if "/geo/" in path or "/directions/" in path or "/routeSearch/" in path:
            location = self._parse_first_lon_lat(path)
            if location is not None:
                return location

        raise TwoGisUrlParseError("2GIS URL does not contain coordinates")

    @staticmethod
    def _is_twogis_host(host: str) -> bool:
        normalized_host = host.rstrip(".").lower()
        for suffix in _TWOGIS_HOST_SUFFIXES:
            if normalized_host == suffix or normalized_host.endswith(f".{suffix}"):
                return True
        return False

    @staticmethod
    def _parse_first_lon_lat(value: str) -> Location | None:
        match = _LON_LAT_PATTERN.search(value)
        if match is None:
            return None

        try:
            longitude = float(match.group("longitude"))
            latitude = float(match.group("latitude"))
            return Location(
                latitude=latitude,
                longitude=longitude,
                source="twogis_url",
            )
        except InvalidLocationError as exc:
            raise TwoGisUrlParseError(str(exc)) from exc


async def parse_twogis_url(value: str) -> Location:
    return await TwoGisUrlParser().parse(value)

