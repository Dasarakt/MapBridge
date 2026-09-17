import logging
import traceback

import httpx
import pytest
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import GetMe

from app.bot.app import TokenSafeAiohttpSession, configure_logging
from app.core.resolver import RedirectResolutionError, RedirectResolver
from app.services.conversion import UnsupportedInputError, create_default_converter
from app.services.geocoding import GeocodingError, GooglePlacesGeocoder, NominatimGeocoder


def _traceback_text(error: BaseException) -> str:
    return "".join(traceback.format_exception(error))


@pytest.mark.asyncio
async def test_info_logging_keeps_app_messages_but_not_http_urls(caplog) -> None:
    httpx_logger = logging.getLogger("httpx")
    httpcore_logger = logging.getLogger("httpcore")
    previous_levels = httpx_logger.level, httpcore_logger.level
    private_url = "https://share.google/private-location-marker"

    try:
        configure_logging("INFO")
        with caplog.at_level(logging.INFO):
            logging.getLogger("app.test").info("application info remains visible")
            async with httpx.AsyncClient(
                transport=httpx.MockTransport(lambda request: httpx.Response(200))
            ) as client:
                await client.get(private_url)
            httpx_logger.warning("HTTP warning remains visible")

        assert "application info remains visible" in caplog.text
        assert "HTTP warning remains visible" in caplog.text
        assert private_url not in caplog.text
        assert httpx_logger.level == logging.WARNING
        assert httpcore_logger.level == logging.WARNING
    finally:
        httpx_logger.setLevel(previous_levels[0])
        httpcore_logger.setLevel(previous_levels[1])


@pytest.mark.asyncio
async def test_short_url_network_error_hides_submitted_url() -> None:
    private_url = "https://share.google/private-location-marker"

    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(f"request failed for {request.url}", request=request)

    resolver = RedirectResolver(
        resolver=lambda host: (host, [], ["8.8.8.8"]),
        transport=httpx.MockTransport(fail),
    )

    with pytest.raises(RedirectResolutionError) as error:
        await resolver.resolve(private_url)

    assert private_url not in _traceback_text(error.value)


@pytest.mark.asyncio
async def test_short_url_invalid_request_hides_submitted_url(monkeypatch) -> None:
    private_url = "https://share.google/private-invalid-marker"

    def fail_build_request(client, method, url):
        raise httpx.InvalidURL(f"invalid URL: {url}")

    monkeypatch.setattr(httpx.AsyncClient, "build_request", fail_build_request)
    resolver = RedirectResolver(resolver=lambda host: (host, [], ["8.8.8.8"]))

    with pytest.raises(RedirectResolutionError) as error:
        await resolver.resolve(private_url)

    assert private_url not in _traceback_text(error.value)


@pytest.mark.asyncio
async def test_nominatim_http_error_hides_query(monkeypatch) -> None:
    private_query = "private-locality-marker"
    original_client = httpx.AsyncClient

    def client(*args, **kwargs):
        return original_client(
            *args,
            transport=httpx.MockTransport(lambda request: httpx.Response(503)),
            **kwargs,
        )

    monkeypatch.setattr(httpx, "AsyncClient", client)

    with pytest.raises(GeocodingError) as error:
        await NominatimGeocoder().search(private_query)

    assert private_query not in _traceback_text(error.value)


@pytest.mark.asyncio
async def test_google_places_network_error_hides_query_and_key() -> None:
    private_query = "private-place-marker"
    fake_key = "fake-places-key-marker"

    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(
            f"request failed for {request.url}: {fake_key} {private_query}",
            request=request,
        )

    geocoder = GooglePlacesGeocoder(
        api_key=fake_key,
        transport=httpx.MockTransport(fail),
    )

    with pytest.raises(GeocodingError) as error:
        await geocoder.search(private_query)

    rendered = _traceback_text(error.value)
    assert private_query not in rendered
    assert fake_key not in rendered


@pytest.mark.asyncio
async def test_unrecognized_text_error_does_not_repeat_input() -> None:
    private_input = "private-location-text-marker"

    with pytest.raises(UnsupportedInputError) as error:
        await create_default_converter().parse(private_input)

    assert private_input not in str(error.value)


@pytest.mark.asyncio
async def test_telegram_network_error_redacts_token(monkeypatch) -> None:
    fake_token = "123456789:FAKE_TOKEN_MARKER"
    method = GetMe()

    async def fail(session, bot, requested_method, timeout=None):
        raise TelegramNetworkError(
            method=requested_method,
            message=f"redirect to https://api.telegram.org/bot{fake_token}/getMe",
        )

    monkeypatch.setattr(AiohttpSession, "make_request", fail)
    bot = type("FakeBot", (), {"token": fake_token})()

    with pytest.raises(TelegramNetworkError) as error:
        await TokenSafeAiohttpSession().make_request(bot, method)

    assert fake_token not in _traceback_text(error.value)
    assert "[REDACTED]" in str(error.value)
