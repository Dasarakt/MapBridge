import pytest

from app.db.connection import connect_postgres


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql://mapbridge:example@postgres:5432/mapbridge",
        "postgresql://mapbridge:bad%secret#part@postgres:5432/mapbridge",
    ],
)
def test_postgres_password_in_url_is_rejected_without_echoing_it(database_url) -> None:
    with pytest.raises(RuntimeError) as error:
        connect_postgres(database_url)

    assert "password" in str(error.value)
    assert "example" not in str(error.value)
    assert "bad%secret" not in str(error.value)
