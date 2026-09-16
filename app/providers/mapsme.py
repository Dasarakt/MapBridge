from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class MapsMeProvider(MapProvider):
    name = "mapsme"
    title = "MAPS.ME"
    supports_import = False
    supports_export = True
    supports_view = True
    supports_navigate = True

    def build_url(self, location: Location) -> str:
        params = [
            ("v", "1"),
            ("ll", f"{location.latitude:.7f},{location.longitude:.7f}"),
        ]
        if location.name:
            params.append(("n", location.name))

        return "https://dlink.maps.me/map?" + urlencode(params)
