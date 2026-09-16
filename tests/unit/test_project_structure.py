from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_checkpoint_zero_files_exist() -> None:
    expected_paths = [
        "README.md",
        "pyproject.toml",
        ".env.example",
        ".gitignore",
        "Dockerfile",
        "docker-compose.yml",
        "main.py",
        "app/__main__.py",
        "app/config.py",
        "app/bot/app.py",
        "app/bot/handlers/start.py",
        "app/core/exceptions.py",
        "app/parsers/base.py",
        "app/providers/base.py",
        "app/services/conversion.py",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
    ]

    missing_paths = [
        path for path in expected_paths if not (PROJECT_ROOT / path).exists()
    ]

    assert missing_paths == []

