from abc import ABC, abstractmethod
from collections.abc import Iterable

import httpx

from app.config import load_settings
from app.core.exceptions import MapBridgeError
from app.core.location import Location


class GeocodingError(MapBridgeError, ValueError):
    """Raised when a place name cannot be geocoded."""


class Geocoder(ABC):
    @abstractmethod
    async def search(self, query: str) -> Location:
        """Find a reference location for a human-readable query."""


class NominatimGeocoder(Geocoder):
    def __init__(
        self,
        base_url: str = "https://nominatim.openstreetmap.org/search",
        timeout_seconds: float = 5.0,
        user_agent: str = "MapBridgeBot/0.1",
    ) -> None:
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._user_agent = user_agent

    async def search(self, query: str) -> Location:
        normalized_query = query.strip()
        if not normalized_query:
            raise GeocodingError("geocoding query is empty")

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.get(
                self._base_url,
                params={
                    "q": normalized_query,
                    "format": "jsonv2",
                    "limit": "1",
                },
                headers={"User-Agent": self._user_agent},
            )
            response.raise_for_status()

        results = response.json()
        if not results:
            raise GeocodingError("place was not found")

        first_result = results[0]
        try:
            return Location(
                latitude=float(first_result["lat"]),
                longitude=float(first_result["lon"]),
                name=first_result.get("display_name"),
                source="nominatim",
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GeocodingError("geocoding response is invalid") from exc


class GooglePlacesGeocoder(Geocoder):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://places.googleapis.com/v1/places:searchText",
        timeout_seconds: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def search(self, query: str) -> Location:
        normalized_query = query.strip()
        if not normalized_query:
            raise GeocodingError("geocoding query is empty")

        if not self._api_key:
            raise GeocodingError("Google Places API key is not configured")

        async with httpx.AsyncClient(
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            response = await client.post(
                self._base_url,
                json={"textQuery": normalized_query},
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self._api_key,
                    "X-Goog-FieldMask": "places.displayName,places.location",
                },
            )
            response.raise_for_status()

        results = response.json().get("places", [])
        if not results:
            raise GeocodingError("place was not found")

        first_result = results[0]
        try:
            location = first_result["location"]
            display_name = first_result.get("displayName", {}).get("text")
            return Location(
                latitude=float(location["latitude"]),
                longitude=float(location["longitude"]),
                name=display_name,
                source="google_places",
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GeocodingError("Google Places response is invalid") from exc


class FallbackGeocoder(Geocoder):
    def __init__(self, geocoders: Iterable[Geocoder]) -> None:
        self._geocoders = list(geocoders)

    async def search(self, query: str) -> Location:
        last_error: GeocodingError | None = None
        for geocoder in self._geocoders:
            try:
                return await geocoder.search(query)
            except GeocodingError as exc:
                last_error = exc

        raise GeocodingError(str(last_error or "place was not found"))


def create_default_geocoder() -> Geocoder:
    settings = load_settings()
    geocoders: list[Geocoder] = []
    if settings.google_places_api_key:
        geocoders.append(GooglePlacesGeocoder(settings.google_places_api_key))
    geocoders.append(NominatimGeocoder())
    return FallbackGeocoder(geocoders)
