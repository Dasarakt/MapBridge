from urllib.parse import urlencode

from app.core.location import Location
from app.providers.base import MapProvider


class YandexNavigatorProvider(MapProvider):
    name = "yandex_navigator"
    title = "Yandex Navigator"
    supports_import = False
    supports_export = True
    supports_view = False
    supports_navigate = True

    def build_url(self, location: Location) -> str:
        return "yandexnavi://show_point_on_map?" + urlencode(
            {
                "lat": f"{location.latitude:.7f}",
                "lon": f"{location.longitude:.7f}",
            }
        )

    def build_navigation_url(self, location: Location) -> str:
        return "yandexnavi://build_route_on_map?" + urlencode(
            {
                "lat_to": f"{location.latitude:.7f}",
                "lon_to": f"{location.longitude:.7f}",
            }
        )

    def build_telegram_url(self, location: Location, action: str = "view") -> str:
        point = f"{location.longitude:.7f},{location.latitude:.7f}"
        zoom = int(location.zoom) if location.zoom is not None else 17
        return "https://yandex.ru/navi/?" + urlencode(
            {
                "whatshere[point]": point,
                "whatshere[zoom]": str(zoom),
                "lang": "ru",
                "from": "navi",
            }
        )
