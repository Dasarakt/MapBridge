from urllib.parse import parse_qs, unquote, urlparse

from app.core.exceptions import MapBridgeError
from app.core.location import InvalidLocationError, Location
from app.parsers.base import LocationParser


class YandexMapsUrlParseError(MapBridgeError, ValueError):
    """Raised when a Yandex Maps URL does not contain parseable coordinates."""


_YANDEX_HOST_SUFFIXES = (
    "yandex.com",
    "yandex.ru",
    "yandex.ge",
    "yandex.by",
    "yandex.kz",
    "yandex.uz",
    "yandex.com.tr",
)
_COORDINATE_QUERY_FIELDS = (
    "ll",
    "pt",
    "whatshere[point]",
)


class YandexMapsUrlParser(LocationParser):
    async def parse(self, value: str) -> Location:
        parsed_url = urlparse(value.strip())
        host = parsed_url.hostname

        if host is None or not self._is_yandex_maps_host(host):
            raise YandexMapsUrlParseError("not a supported Yandex Maps URL")

        query = parse_qs(parsed_url.query)
        for field in _COORDINATE_QUERY_FIELDS:
            for candidate in query.get(field, []):
                location = self._parse_lon_lat(candidate)
                if location is not None:
                    return location

        raise YandexMapsUrlParseError("Yandex Maps URL does not contain coordinates")

    @staticmethod
    def _is_yandex_maps_host(host: str) -> bool:
        normalized_host = host.rstrip(".").lower()
        for suffix in _YANDEX_HOST_SUFFIXES:
            if normalized_host == suffix or normalized_host.endswith(f".{suffix}"):
                return True
        return False

    @staticmethod
    def _parse_lon_lat(value: str) -> Location | None:
        parts = unquote(value).split(",", maxsplit=1)
        if len(parts) != 2:
            return None

        longitude_text, latitude_text = parts
        try:
            longitude = float(longitude_text)
            latitude = float(latitude_text)
            return Location(
                latitude=latitude,
                longitude=longitude,
                source="yandex_maps_url",
            )
        except ValueError:
            return None
        except InvalidLocationError as exc:
            raise YandexMapsUrlParseError(str(exc)) from exc


async def parse_yandex_maps_url(value: str) -> Location:
    return await YandexMapsUrlParser().parse(value)

