from app.core.location import Location
from app.providers.base import MapProvider


class TwoGisProvider(MapProvider):
    name = "twogis"
    title = "2GIS"
    supports_import = False
    supports_export = True

    def build_url(self, location: Location) -> str:
        return (
            "https://2gis.com/geo/"
            f"{location.longitude:.7f},{location.latitude:.7f}"
        )

