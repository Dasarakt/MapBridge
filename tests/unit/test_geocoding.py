import httpx
import pytest

from app.core.location import Location
from app.services.geocoding import (
    FallbackGeocoder,
    Geocoder,
    GeocodingError,
    GooglePlacesGeocoder,
    NominatimGeocoder,
)


class AlwaysFailingGeocoder(Geocoder):
    async def search(self, query: str) -> Location:
        raise GeocodingError("place was not found")


class StaticGeocoder(Geocoder):
    async def search(self, query: str) -> Location:
        return Location(latitude=41.0, longitude=44.0, source="static")


@pytest.mark.asyncio
async def test_nominatim_geocoder_parses_first_result(monkeypatch) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json=[
                {
                    "lat": "42.4435",
                    "lon": "42.3915",
                    "display_name": "Didi Inchkhuri, Georgia",
                }
            ],
        )

    transport = httpx.MockTransport(handler)
    original_async_client = httpx.AsyncClient

    def patched_async_client(*args, **kwargs):
        return original_async_client(*args, transport=transport, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

    geocoder = NominatimGeocoder(user_agent="MapBridgeBot/test")
    location = await geocoder.search("Didi Inchkhuri")

    assert location.latitude == 42.4435
    assert location.longitude == 42.3915
    assert location.name == "Didi Inchkhuri, Georgia"
    assert requests[0].headers["user-agent"] == "MapBridgeBot/test"
    assert "format=jsonv2" in str(requests[0].url)
    assert "limit=1" in str(requests[0].url)


@pytest.mark.asyncio
async def test_nominatim_geocoder_raises_when_place_is_not_found(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(handler)
    original_async_client = httpx.AsyncClient

    def patched_async_client(*args, **kwargs):
        return original_async_client(*args, transport=transport, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

    with pytest.raises(GeocodingError):
        await NominatimGeocoder().search("not a real place")


@pytest.mark.asyncio
async def test_google_places_geocoder_parses_first_result() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "places": [
                    {
                        "displayName": {"text": "Kutaisi Cable Car Bottom Station"},
                        "location": {
                            "latitude": 42.2701413,
                            "longitude": 42.6990378,
                        },
                    }
                ]
            },
        )

    geocoder = GooglePlacesGeocoder(
        api_key="places-key",
        transport=httpx.MockTransport(handler),
    )

    location = await geocoder.search("Kutaisi Cable Car Bottom Station")

    assert location.latitude == 42.2701413
    assert location.longitude == 42.6990378
    assert location.name == "Kutaisi Cable Car Bottom Station"
    assert requests[0].headers["x-goog-api-key"] == "places-key"
    assert (
        requests[0].headers["x-goog-fieldmask"]
        == "places.displayName,places.location"
    )


@pytest.mark.asyncio
async def test_google_places_geocoder_raises_when_place_is_not_found() -> None:
    geocoder = GooglePlacesGeocoder(
        api_key="places-key",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={})),
    )

    with pytest.raises(GeocodingError):
        await geocoder.search("not a real place")


@pytest.mark.asyncio
async def test_fallback_geocoder_uses_next_geocoder_after_failure() -> None:
    geocoder = FallbackGeocoder([AlwaysFailingGeocoder(), StaticGeocoder()])

    location = await geocoder.search("place")

    assert location.latitude == 41.0
    assert location.longitude == 44.0
