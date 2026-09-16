import httpx
import pytest

from app.core.resolver import RedirectResolutionError, RedirectResolver


def public_resolver(host: str) -> tuple[str, list[str], list[str]]:
    return (host, [], ["8.8.8.8"])


def private_resolver(host: str) -> tuple[str, list[str], list[str]]:
    return (host, [], ["127.0.0.1"])


@pytest.mark.asyncio
async def test_redirect_resolver_follows_allowed_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://maps.app.goo.gl/example":
            return httpx.Response(
                302,
                headers={
                    "location": "https://www.google.com/maps/@41.6935000,44.8015790,17z"
                },
            )
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)

    resolver = RedirectResolver(
        resolver=public_resolver,
        transport=transport,
    )

    final_url = await resolver.resolve("https://maps.app.goo.gl/example")

    assert final_url == "https://www.google.com/maps/@41.6935000,44.8015790,17z"


@pytest.mark.asyncio
async def test_redirect_resolver_allows_share_google_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://share.google/example":
            return httpx.Response(
                302,
                headers={
                    "location": "https://www.google.com/maps/@41.6935000,44.8015790,17z"
                },
            )
        return httpx.Response(200)

    resolver = RedirectResolver(
        resolver=public_resolver,
        transport=httpx.MockTransport(handler),
    )

    final_url = await resolver.resolve("https://share.google/example")

    assert final_url == "https://www.google.com/maps/@41.6935000,44.8015790,17z"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://maps.app.goo.gl/example",
        "https://example.com/maps",
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/",
    ],
)
@pytest.mark.asyncio
async def test_redirect_resolver_rejects_unsafe_urls(url: str) -> None:
    resolver = RedirectResolver(
        allowed_hosts={
            "maps.app.goo.gl",
            "127.0.0.1",
            "localhost",
            "169.254.169.254",
        },
        resolver=private_resolver,
    )

    with pytest.raises(RedirectResolutionError):
        await resolver.resolve(url)


@pytest.mark.asyncio
async def test_redirect_resolver_rejects_redirect_to_unallowed_host() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "https://example.com/maps"})

    resolver = RedirectResolver(
        resolver=public_resolver,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(RedirectResolutionError):
        await resolver.resolve("https://maps.app.goo.gl/example")


@pytest.mark.asyncio
async def test_redirect_resolver_rejects_redirect_loop() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": str(request.url)})

    resolver = RedirectResolver(
        max_redirects=1,
        resolver=public_resolver,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(RedirectResolutionError, match="too many redirects"):
        await resolver.resolve("https://maps.app.goo.gl/example")
