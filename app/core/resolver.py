import ipaddress
import socket
from collections.abc import Callable
from urllib.parse import urljoin, urlparse

import httpx

from app.core.exceptions import MapBridgeError


class RedirectResolutionError(MapBridgeError, ValueError):
    """Raised when a URL cannot be safely resolved."""


DEFAULT_ALLOWED_HOSTS = {
    "maps.app.goo.gl",
    "share.google",
    "goo.gl",
    "google.com",
    "www.google.com",
    "maps.google.com",
}


class RedirectResolver:
    def __init__(
        self,
        allowed_hosts: set[str] | None = None,
        max_redirects: int = 5,
        timeout_seconds: float = 5.0,
        resolver: Callable[[str], list[str]] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._allowed_hosts = allowed_hosts or DEFAULT_ALLOWED_HOSTS
        self._max_redirects = max_redirects
        self._timeout_seconds = timeout_seconds
        self._resolver = resolver or socket.gethostbyname_ex
        self._transport = transport

    async def resolve(self, value: str) -> str:
        current_url = value.strip()
        self._validate_url(current_url)

        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            for _ in range(self._max_redirects + 1):
                request = client.build_request("GET", current_url)
                response = await client.send(request, stream=True)
                try:
                    if not response.is_redirect:
                        return str(response.url)

                    location = response.headers.get("location")
                    if not location:
                        raise RedirectResolutionError(
                            "redirect response has no Location"
                        )

                    next_url = urljoin(str(response.url), location)
                    self._validate_url(next_url)
                    current_url = next_url
                finally:
                    await response.aclose()

        raise RedirectResolutionError("too many redirects")

    def _validate_url(self, value: str) -> None:
        parsed_url = urlparse(value)
        host = parsed_url.hostname

        if parsed_url.scheme not in {"http", "https"}:
            raise RedirectResolutionError("only http and https URLs are allowed")

        if host is None:
            raise RedirectResolutionError("URL host is required")

        normalized_host = host.rstrip(".").lower()
        if normalized_host not in self._allowed_hosts:
            raise RedirectResolutionError("URL host is not allowed")

        for address in self._resolve_host(normalized_host):
            if self._is_private_address(address):
                raise RedirectResolutionError("URL resolves to a private address")

    def _resolve_host(self, host: str) -> list[str]:
        try:
            result = self._resolver(host)
        except socket.gaierror as exc:
            raise RedirectResolutionError("URL host cannot be resolved") from exc

        if isinstance(result, tuple):
            return list(result[2])

        return list(result)

    @staticmethod
    def _is_private_address(value: str) -> bool:
        address = ipaddress.ip_address(value)
        return (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_multicast
            or address.is_reserved
            or address.is_unspecified
        )
