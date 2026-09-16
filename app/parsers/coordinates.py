import re

from app.core.exceptions import MapBridgeError
from app.core.location import InvalidLocationError, Location
from app.parsers.base import LocationParser


class CoordinatesParseError(MapBridgeError, ValueError):
    """Raised when text does not contain a valid decimal coordinate pair."""


_NUMBER_PATTERN = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
_COORDINATE_PAIR_PATTERN = re.compile(
    rf"(?<![\w.])(?P<latitude>{_NUMBER_PATTERN})(?:\s*,\s*|\s+)"
    rf"(?P<longitude>{_NUMBER_PATTERN})(?![\w.])"
)


class DecimalCoordinatesParser(LocationParser):
    async def parse(self, value: str) -> Location:
        for match in _COORDINATE_PAIR_PATTERN.finditer(value.strip()):
            latitude = float(match.group("latitude"))
            longitude = float(match.group("longitude"))

            try:
                return Location(
                    latitude=latitude,
                    longitude=longitude,
                    source="coordinates",
                )
            except InvalidLocationError as exc:
                raise CoordinatesParseError(str(exc)) from exc

        raise CoordinatesParseError("text does not contain decimal coordinates")


def parse_decimal_coordinates(value: str) -> Location:
    for match in _COORDINATE_PAIR_PATTERN.finditer(value.strip()):
        latitude = float(match.group("latitude"))
        longitude = float(match.group("longitude"))

        try:
            return Location(
                latitude=latitude,
                longitude=longitude,
                source="coordinates",
            )
        except InvalidLocationError as exc:
            raise CoordinatesParseError(str(exc)) from exc

    raise CoordinatesParseError("text does not contain decimal coordinates")
