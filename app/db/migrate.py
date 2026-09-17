from app.config import load_settings
from app.db.connection import connect_postgres
from app.db.migrations import MIGRATIONS


def migrate(database_url: str, password: str = "") -> None:
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL migrations")

    with connect_postgres(database_url, password) as connection:
        connection.execute("SELECT pg_advisory_xact_lock(724191260)")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY
            )
            """
        )
        applied = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        unknown = applied - MIGRATIONS.keys()
        if unknown:
            raise RuntimeError(f"Unknown PostgreSQL schema version: {min(unknown)}")

        for version, statements in sorted(MIGRATIONS.items()):
            if version in applied:
                continue
            for statement in statements:
                connection.execute(statement)
            connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (version,),
            )


if __name__ == "__main__":
    settings = load_settings()
    migrate(settings.database_url, settings.postgres_password)
