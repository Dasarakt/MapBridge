import pytest

from app.parsers.coordinates import CoordinatesParseError, parse_decimal_coordinates


@pytest.mark.parametrize(
    ("value", "expected_latitude", "expected_longitude"),
    [
        ("42.4439296, 42.3915008", 42.4439296, 42.3915008),
        ("42.4439296 42.3915008", 42.4439296, 42.3915008),
        ("42.4439296,42.3915008", 42.4439296, 42.3915008),
        (
            "Отель - 42.4439296, 42.3915008, Мартвили 3100",
            42.4439296,
            42.3915008,
        ),
    ],
)
def test_parse_decimal_coordinates(
    value: str,
    expected_latitude: float,
    expected_longitude: float,
) -> None:
    location = parse_decimal_coordinates(value)

    assert location.latitude == expected_latitude
    assert location.longitude == expected_longitude
    assert location.source == "coordinates"


@pytest.mark.parametrize(
    "value",
    [
        "999, 999",
        "hello world",
        "",
    ],
)
def test_parse_decimal_coordinates_rejects_invalid_input(value: str) -> None:
    with pytest.raises(CoordinatesParseError):
        parse_decimal_coordinates(value)


def test_parse_decimal_coordinates_uses_first_valid_pair() -> None:
    location = parse_decimal_coordinates(
        "first 42.4439296, 42.3915008 second 41.1, 44.8"
    )

    assert location.latitude == 42.4439296
    assert location.longitude == 42.3915008

