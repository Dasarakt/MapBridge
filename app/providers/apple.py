from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class AppleMapsProvider(MapProvider):
    name = "apple"
    title = "Apple Maps"
    supports_import = False
    supports_export = True

    def build_url(self, location: Location) -> str:
        coordinates = f"{location.latitude:.7f},{location.longitude:.7f}"
        return "https://maps.apple.com/?" + urlencode(
            {
                "ll": coordinates,
                "q": coordinates,
            }
        )

