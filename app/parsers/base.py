from abc import ABC, abstractmethod

from app.core.location import Location


class LocationParser(ABC):
    @abstractmethod
    async def parse(self, value: str) -> Location:
        """Parse a value into a normalized location."""
