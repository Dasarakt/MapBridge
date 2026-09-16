from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import InvalidLocationError, Location
from app.parsers.base import LocationParser
from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


class OpenStreetMapUrlParseError(MapBridgeError, ValueError):
    """Raised when an OpenStreetMap URL does not contain parseable coordinates."""


_OSM_HOSTS = {
    "openstreetmap.org",
    "www.openstreetmap.org",
}


class OpenStreetMapUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host not in _OSM_HOSTS:
            raise OpenStreetMapUrlParseError("not a supported OpenStreetMap URL")

        query = parse_qs(parsed_url.query)
        location = self._parse_marker_coordinates(query)
        if location is not None:
            return location

        for candidate in query.get("query", []):
            location = self._parse_coordinate_text(candidate)
            if location is not None:
                return location

        location = self._parse_hash_coordinates(parsed_url.fragment)
        if location is not None:
            return location

        raise OpenStreetMapUrlParseError(
            "OpenStreetMap URL does not contain coordinates"
        )

    def _parse_marker_coordinates(
        self,
        query: dict[str, list[str]],
    ) -> Location | None:
        latitudes = query.get("mlat", [])
        longitudes = query.get("mlon", [])
        if not latitudes or not longitudes:
            return None

        try:
            return self._build_location(float(latitudes[0]), float(longitudes[0]))
        except ValueError:
            return None

    def _parse_hash_coordinates(self, fragment: str) -> Location | None:
        parts = unquote(fragment).split("/")
        if len(parts) < 3 or not parts[0].startswith("map="):
            return None

        try:
            return self._build_location(float(parts[1]), float(parts[2]))
        except ValueError:
            return None

    def _parse_coordinate_text(self, value: str) -> Location | None:
        try:
            location = parse_decimal_coordinates(value)
        except CoordinatesParseError:
            return None

        return self._build_location(location.latitude, location.longitude)

    @staticmethod
    def _build_location(latitude: float, longitude: float) -> Location:
        try:
            return Location(
                latitude=latitude,
                longitude=longitude,
                source="osm_url",
            )
        except InvalidLocationError as exc:
            raise OpenStreetMapUrlParseError(str(exc)) from exc


async def parse_osm_url(value: str) -> Location:
    return await OpenStreetMapUrlParser().parse(value)
