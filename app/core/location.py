from dataclasses import dataclass

from app.core.exceptions import MapBridgeError


class InvalidLocationError(MapBridgeError, ValueError):
    """Raised when latitude or longitude is outside the supported range."""


@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None
    zoom: float | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        self._validate_coordinate("latitude", self.latitude, -90, 90)
        self._validate_coordinate("longitude", self.longitude, -180, 180)

    @staticmethod
    def _validate_coordinate(
        field_name: str,
        value: float,
        minimum: float,
        maximum: float,
    ) -> None:
        if not minimum <= value <= maximum:
            raise InvalidLocationError(
                f"{field_name} must be between {minimum} and {maximum}"
            )

