import psycopg


def connect_postgres(database_url: str, password: str = "", **kwargs):
    if not database_url.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("DATABASE_URL must be a PostgreSQL URL")

    authority = database_url.split("://", 1)[1]
    userinfo, separator, _ = authority.partition("@")
    if separator and ":" in userinfo:
        raise RuntimeError(
            "DATABASE_URL must not contain a password; set POSTGRES_PASSWORD separately"
        )

    try:
        return psycopg.connect(
            database_url,
            password=password or None,
            connect_timeout=5,
            **kwargs,
        )
    except psycopg.ProgrammingError:
        raise RuntimeError("Invalid password-free DATABASE_URL") from None
