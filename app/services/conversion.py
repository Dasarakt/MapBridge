from collections.abc import Iterable

from app.core.exceptions import MapBridgeError
from app.core.location import Location
from app.parsers.apple_url import AppleMapsUrlParser
from app.parsers.base import LocationParser
from app.parsers.coordinates import DecimalCoordinatesParser
from app.parsers.google_url import GoogleMapsUrlParser
from app.parsers.here_url import HereUrlParser
from app.parsers.mapsme_url import MapsMeUrlParser
from app.parsers.osmand_url import OsmAndUrlParser
from app.parsers.osm_url import OpenStreetMapUrlParser
from app.parsers.organic_maps_url import OrganicMapsUrlParser
from app.parsers.plus_code import PlusCodeParser
from app.parsers.twogis_url import TwoGisUrlParser
from app.parsers.waze_url import WazeUrlParser
from app.parsers.yandex_url import YandexMapsUrlParser
from app.providers.apple import AppleMapsProvider
from app.providers.base import MapAction, MapLink, MapProvider
from app.providers.google import GoogleMapsProvider
from app.providers.mapsme import MapsMeProvider
from app.providers.organic_maps import OrganicMapsProvider
from app.providers.osm import OpenStreetMapProvider
from app.providers.twogis import TwoGisProvider
from app.providers.waze import WazeProvider
from app.providers.yandex import YandexMapsProvider
from app.providers.yandex_navigator import YandexNavigatorProvider


class UnsupportedInputError(MapBridgeError, ValueError):
    """Raised when input cannot be converted into a location yet."""


def default_providers() -> list[MapProvider]:
    return [
        GoogleMapsProvider(),
        YandexMapsProvider(),
        AppleMapsProvider(),
        TwoGisProvider(),
        OpenStreetMapProvider(),
        OrganicMapsProvider(),
        MapsMeProvider(),
        YandexNavigatorProvider(),
        WazeProvider(),
    ]


class LocationConverter:
    def __init__(
        self,
        parsers: Iterable[LocationParser] | None = None,
        providers: Iterable[MapProvider] | None = None,
    ) -> None:
        self._parsers = list(
            parsers
            or [
                GoogleMapsUrlParser(),
                YandexMapsUrlParser(),
                AppleMapsUrlParser(),
                TwoGisUrlParser(),
                OpenStreetMapUrlParser(),
                WazeUrlParser(),
                OrganicMapsUrlParser(),
                MapsMeUrlParser(),
                HereUrlParser(),
                OsmAndUrlParser(),
                PlusCodeParser(),
                DecimalCoordinatesParser(),
            ]
        )
        self._providers = list(providers or default_providers())

    async def parse(self, value: str) -> Location:
        for parser in self._parsers:
            try:
                return await parser.parse(value)
            except MapBridgeError:
                continue

        raise UnsupportedInputError("unsupported location input")

    def get_links(
        self,
        location: Location,
        provider_names: Iterable[str] | None = None,
        action: MapAction | None = None,
    ) -> list[MapLink]:
        provider_filter = set(provider_names) if provider_names is not None else None
        actions: tuple[MapAction, ...]
        if action is None:
            actions = ("view", "navigate")
        else:
            actions = (action,)

        links: list[MapLink] = []
        for provider in self._providers:
            if not provider.supports_export:
                continue
            if provider_filter is not None and provider.name not in provider_filter:
                continue

            if "view" in actions and provider.supports_view:
                links.append(provider.build_link(location, action="view"))
            if "navigate" in actions and provider.supports_navigate:
                links.append(provider.build_link(location, action="navigate"))

        return [
            link
            for link in links
        ]


def create_default_converter() -> LocationConverter:
    return LocationConverter()
