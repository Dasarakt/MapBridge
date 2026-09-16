FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .


FROM base AS test

RUN python -m pip install --no-cache-dir ".[dev]"

COPY .env.example .gitignore Dockerfile docker-compose.yml main.py ./
COPY tests ./tests

CMD ["python", "-m", "pytest", "-q"]


FROM base AS runtime

CMD ["python", "-m", "app"]
