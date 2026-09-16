import re

from openlocationcode import openlocationcode as olc

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.base import LocationParser
from app.services.geocoding import Geocoder, GeocodingError, create_default_geocoder


class PlusCodeParseError(MapBridgeError, ValueError):
    """Raised when text does not contain a valid full Plus Code."""


_PLUS_CODE_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?P<code>[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3})(?![A-Z0-9])",
    re.IGNORECASE,
)


class PlusCodeParser(LocationParser):
    def __init__(self, geocoder: Geocoder | None = None) -> None:
        self._geocoder = geocoder or create_default_geocoder()

    async def parse(self, value: str) -> Location:
        text = value.strip()
        for match in _PLUS_CODE_PATTERN.finditer(text):
            code = match.group("code").upper()
            if not olc.isValid(code):
                continue

            if not olc.isFull(code):
                return await self._parse_short_code(code, text[match.end() :])

            area = olc.decode(code)
            return Location(
                latitude=area.latitudeCenter,
                longitude=area.longitudeCenter,
                source="plus_code",
            )

        raise PlusCodeParseError("text does not contain a full Plus Code")

    async def _parse_short_code(self, code: str, locality: str) -> Location:
        normalized_locality = locality.strip(" ,;-")
        if not normalized_locality:
            raise PlusCodeParseError("short Plus Codes require a locality")

        try:
            reference = await self._geocoder.search(normalized_locality)
        except GeocodingError as exc:
            raise PlusCodeParseError(str(exc)) from exc

        recovered_code = olc.recoverNearest(
            code,
            reference.latitude,
            reference.longitude,
        )
        area = olc.decode(recovered_code)
        return Location(
            latitude=area.latitudeCenter,
            longitude=area.longitudeCenter,
            address=normalized_locality,
            source="plus_code",
        )


async def parse_plus_code(value: str) -> Location:
    return await PlusCodeParser().parse(value)
