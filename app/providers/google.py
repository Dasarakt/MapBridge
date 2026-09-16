from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class GoogleMapsProvider(MapProvider):
    name = "google"
    title = "Google Maps"
    supports_import = False
    supports_export = True

    def build_url(self, location: Location) -> str:
        query = f"{location.latitude:.7f},{location.longitude:.7f}"
        return "https://www.google.com/maps/search/?" + urlencode(
            {
                "api": "1",
                "query": query,
            }
        )

