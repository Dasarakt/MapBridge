from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class OpenStreetMapProvider(MapProvider):
    name = "osm"
    title = "OpenStreetMap"
    supports_import = False
    supports_export = True

    def build_url(self, location: Location) -> str:
        latitude = f"{location.latitude:.7f}"
        longitude = f"{location.longitude:.7f}"
        zoom = int(location.zoom) if location.zoom is not None else 17
        query = urlencode(
            {
                "mlat": latitude,
                "mlon": longitude,
            }
        )
        return (
            "https://www.openstreetmap.org/?"
            f"{query}#map={zoom}/{latitude}/{longitude}"
        )

