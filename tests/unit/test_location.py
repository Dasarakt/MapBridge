import pytest

from app.core.location import InvalidLocationError, Location


def test_location_accepts_valid_coordinates() -> None:
    location = Location(latitude=42.4439724, longitude=42.3914689)

    assert location.latitude == 42.4439724
    assert location.longitude == 42.3914689
    assert location.name is None


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [
        (91, 42),
        (-91, 42),
        (42, 181),
        (42, -181),
    ],
)
def test_location_rejects_coordinates_outside_supported_ranges(
    latitude: float,
    longitude: float,
) -> None:
    with pytest.raises(InvalidLocationError):
        Location(latitude=latitude, longitude=longitude)


def test_location_preserves_optional_metadata() -> None:
    location = Location(
        latitude=42.4439724,
        longitude=42.3914689,
        name="hotel pillows",
        address="Martvili",
        zoom=17,
        source="test",
    )

    assert location.name == "hotel pillows"
    assert location.address == "Martvili"
    assert location.zoom == 17
    assert location.source == "test"

