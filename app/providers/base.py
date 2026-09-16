from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from app.core.location import Location


MapAction = Literal["view", "navigate"]


@dataclass(frozen=True)
class MapLink:
    provider: str
    title: str
    url: str
    action: MapAction = "view"


class MapProvider(ABC):
    name: str
    title: str
    supports_import: bool = False
    supports_export: bool = True
    supports_view: bool = True
    supports_navigate: bool = False

    @abstractmethod
    def build_url(self, location: Location) -> str:
        """Build a URL that opens the location in this provider."""

    def build_navigation_url(self, location: Location) -> str:
        """Build a URL that starts navigation to the location."""
        return self.build_url(location)

    def build_telegram_url(self, location: Location, action: MapAction = "view") -> str:
        """Build a Telegram inline-keyboard safe URL for the action."""
        if action == "navigate":
            return self.build_navigation_url(location)

        return self.build_url(location)

    def build_link(self, location: Location, action: MapAction = "view") -> MapLink:
        return MapLink(
            provider=self.name,
            title=self.title,
            url=self.build_telegram_url(location, action),
            action=action,
        )
