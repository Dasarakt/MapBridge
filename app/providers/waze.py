from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class WazeProvider(MapProvider):
    name = "waze"
    title = "Waze"
    supports_import = False
    supports_export = True
    supports_view = False
    supports_navigate = True

    def build_url(self, location: Location) -> str:
        coordinates = f"{location.latitude:.7f},{location.longitude:.7f}"
        zoom = int(location.zoom) if location.zoom is not None else 17
        return "https://waze.com/ul?" + urlencode(
            {
                "ll": coordinates,
                "zoom": str(zoom),
            }
        )

    def build_navigation_url(self, location: Location) -> str:
        coordinates = f"{location.latitude:.7f},{location.longitude:.7f}"
        zoom = int(location.zoom) if location.zoom is not None else 17
        return "https://waze.com/ul?" + urlencode(
            {
                "ll": coordinates,
                "navigate": "yes",
                "zoom": str(zoom),
            }
        )
