# MapBridge Bot

MapBridge is a Telegram bot that will convert location input from maps,
coordinates, Plus Codes, and native Telegram locations into links for multiple
map providers.

This repository currently contains the early checkpoints: project skeleton,
location model, decimal coordinates parser, Google Maps URL import, Google Maps
short link resolution, Yandex Maps URL import, Apple Maps URL import, 2GIS URL
import, map URL export providers, a Telegram text handler for coordinates, and
native Telegram Location handling. Full Plus Codes and short Plus Codes with
locality are supported. OpenStreetMap, Waze, Organic Maps, MAPS.ME, HERE WeGo,
and OsmAnd URL imports are supported. SQLite-backed settings are supported for
favorite maps and language selection. Map links are grouped by action: viewing
a point on a map and navigating to it.

## Requirements

- Python 3.12+
- Docker / Docker Compose for containerized runs

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Test

Use one standard command for the project:

```bash
pytest
```

## Run Locally

Create a local environment file:

```bash
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN` in `.env`, then run:

```bash
python -m app
```

Optional local settings database path:

```env
DATABASE_PATH=mapbridge.sqlite3
```

Optional Google Places API key for better `share.google` place resolution:

```env
GOOGLE_PLACES_API_KEY=your-google-places-api-key
```

Without this key, Google place share links are resolved best-effort through the
free geocoder, which may not know every Google-only business or landmark name.

The bot currently responds to `/start`, `/help`, decimal coordinates such as:

```text
42.4439296, 42.3915008
```

It also accepts native Telegram Location messages.

Use `/settings` in private chat to choose personal favorite maps, favorite
navigation apps, and override the interface language. Use `/settings` in a
group, supergroup, or channel to configure that chat's maps, navigation apps,
and language. Shared chat settings are used for automatic replies to recognized
locations in that chat.

The bot stores only Telegram user IDs, chat IDs, and settings. It does not store
submitted coordinates, URLs, or location history.

Long Google Maps URLs with embedded coordinates, `maps.app.goo.gl` short links,
`share.google` links, Yandex Maps URLs with coordinate query parameters, and
Apple Maps URLs with coordinate query parameters are supported. 2GIS URLs with coordinate path
segments such as `/geo/lon,lat` are also supported.
OpenStreetMap URLs with `mlat/mlon`, `#map=zoom/lat/lon`, or coordinate search
queries are supported.
Waze, Organic Maps, MAPS.ME, HERE WeGo, and OsmAnd URLs are supported when they
contain explicit coordinates. Navigation export links include Yandex Navigator,
Waze, Organic Maps, and MAPS.ME.

Full Plus Codes such as `8HH4C9VR+MC` are decoded locally through the Open
Location Code library. Short Plus Codes with locality, such as
`C9VR+MC Didi Inchkhuri`, use a geocoder to find a reference location before
recovering the full code.

The default geocoder backend is Nominatim. Keep usage modest and follow the
Nominatim usage policy, including a custom User-Agent and no heavy traffic.

## Run With Docker Compose

```bash
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN` in `.env`, then run:

```bash
docker compose up --build
```

Stop the container:

```bash
docker compose down
```

## Current Verification Path

For now, use local Python 3.12 + `.venv` + `pytest` as the primary verification
path. Docker files are kept valid, but Docker build/runtime checks are reserved
for a later dedicated checkpoint.

To inspect Docker Compose configuration without printing secrets from `.env`,
use:

```bash
docker compose config --no-env-resolution
```

## Telegram Group And Channel Notes

Groups and supergroups do not require bot admin rights for basic map replies,
but the bot must be allowed to receive the relevant messages. If BotFather
Group Privacy is enabled, Telegram only sends commands, replies, mentions, and
some service-style updates to the bot. Disable Group Privacy if the bot should
react to every coordinate or map link in the group.

Channels require adding the bot as an administrator so Telegram can deliver
channel posts to it and so the bot can publish replies. No special admin rights
are needed beyond posting/reading channel posts for the current feature set.
