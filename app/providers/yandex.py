from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class YandexMapsProvider(MapProvider):
    name = "yandex"
    title = "Yandex Maps"
    supports_import = False
    supports_export = True

    def build_url(self, location: Location) -> str:
        coordinates = f"{location.longitude:.7f},{location.latitude:.7f}"
        zoom = int(location.zoom) if location.zoom is not None else 17
        return "https://yandex.com/maps/?" + urlencode(
            {
                "ll": coordinates,
                "pt": coordinates,
                "z": str(zoom),
            }
        )

