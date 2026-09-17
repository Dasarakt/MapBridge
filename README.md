<p align="center">
  <img src="assets/mapbridge-logo.png" alt="MapBridge" width="420">
</p>

<h1 align="center">MapBridge</h1>

<p align="center">
  Convert locations between map and navigation services.
</p>

<p align="center">
  <a href="https://t.me/bridgemap_bot">Telegram Bot</a> ·
  <a href="https://hub.docker.com/r/dasarakt/mapbridge">Docker Hub</a> ·
  <a href="LICENSE">AGPL-3.0</a>
</p>

## About

MapBridge is an open-source Telegram bot for converting locations between map
and navigation services.

Send it coordinates, a map link, a Plus Code, or a native Telegram Location,
and MapBridge converts the input into a common location representation and
generates links for supported map and navigation apps.

Instead of implementing individual conversions such as Google Maps → Yandex
Maps or Apple Maps → OpenStreetMap, MapBridge uses a provider-independent
location model:

```text
Input
  ↓
Parser / Resolver
  ↓
Location (latitude, longitude, metadata)
  ↓
Providers
  ↓
Map and navigation links
```

This makes it possible to add new input formats and providers without creating
a separate converter for every pair of services.

## Features

- Convert decimal coordinates
- Convert native Telegram Location messages
- Import locations from supported map URLs
- Resolve Google Maps short links
- Decode full Plus Codes locally
- Resolve short Plus Codes with locality
- Generate links for multiple map providers
- Separate **View** and **Navigate** actions
- Personal map and navigation preferences
- Per-chat settings for groups, supergroups, and channels
- Configurable interface language
- SQLite-backed settings persistence
- Docker and Docker Compose support
- Multi-platform Docker images for `linux/amd64` and `linux/arm64`

## Supported Inputs

| Input | Support |
| --- | :---: |
| Decimal coordinates | ✅ |
| Telegram Location | ✅ |
| Full Plus Code | ✅ |
| Short Plus Code + locality | ✅ |
| Google Maps | ✅ |
| Google Maps short links (`maps.app.goo.gl`) | ✅ |
| Google share links (`share.google`) | Best effort |
| Yandex Maps | ✅ |
| Apple Maps | ✅ |
| 2GIS | ✅ |
| OpenStreetMap | ✅ |
| Waze | ✅ |
| Organic Maps | ✅ |
| MAPS.ME | ✅ |
| HERE WeGo | ✅ |
| OsmAnd | ✅ |

URL imports require the source to expose enough information to determine the
location. Some share links may require an external lookup before coordinates
can be resolved.

## Supported Outputs

MapBridge separates opening a location on a map from starting navigation.

### View

Map links are generated for supported map providers, including:

- Google Maps
- Yandex Maps
- Apple Maps
- 2GIS
- OpenStreetMap
- Organic Maps
- MAPS.ME

### Navigate

Navigation links are generated for supported navigation providers, including:

- Yandex Navigator
- Waze
- Organic Maps
- MAPS.ME

The available buttons can be customized through `/settings`.

## Examples

Coordinates:

```text
41.890210, 12.492231
```

Full Plus Code:

```text
8HH4C9VR+MC
```

Short Plus Code with locality:

```text
C9VR+MC Didi Inchkhuri
```

Google Maps short link:

```text
https://maps.app.goo.gl/...
```

You can also send a location directly using Telegram's native Location
attachment.

## Telegram Bot

MapBridge is available on Telegram as
[@bridgemap_bot](https://t.me/bridgemap_bot).

Available commands:

| Command | Description |
| --- | --- |
| `/start` | Start the bot |
| `/help` | Show usage information |
| `/settings` | Configure maps, navigation apps, and language |

### Groups and Channels

MapBridge can also process recognized locations in group chats.

Personal settings are used in private conversations. Groups, supergroups, and
channels can have their own map, navigation, and language settings.

If Telegram Bot Privacy Mode is enabled, Telegram limits which group messages
are delivered to the bot. Disable Group Privacy through BotFather if MapBridge
should automatically process ordinary map links and coordinates posted in a
group.

For channels, the bot must have the permissions required by Telegram to receive
channel posts and publish responses.

## Docker

Official images are published on Docker Hub:

```text
dasarakt/mapbridge
```

Pull the current release:

```bash
docker pull dasarakt/mapbridge:0.1.0
```

Or pull the latest published image:

```bash
docker pull dasarakt/mapbridge:latest
```

Published images support:

```text
linux/amd64
linux/arm64
```

### Docker Compose

Clone the repository and create the environment file:

```bash
cp .env.example .env
```

Set at least:

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

Then start MapBridge:

```bash
docker compose up -d --build
```

View logs:

```bash
docker compose logs -f mapbridge-bot
```

Stop the bot:

```bash
docker compose down
```

The current development Compose configuration builds MapBridge from the local
source tree. Published Docker Hub images can be used directly when deploying
MapBridge without a source build.

## Running from Source

MapBridge requires Python 3.12 or newer.

Create a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install MapBridge with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Create the environment file:

```bash
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN`, then run:

```bash
python -m app
```

## Configuration

MapBridge reads configuration from environment variables and automatically
loads a local `.env` file when present.

| Variable | Required | Description |
| --- | :---: | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram Bot API token |
| `LOG_LEVEL` | No | Application logging level |
| `DATABASE_PATH` | No | Path to the SQLite settings database |
| `GOOGLE_PLACES_API_KEY` | No | Google Places API key for improved `share.google` resolution |

Example:

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
LOG_LEVEL=INFO
DATABASE_PATH=mapbridge.sqlite3
```

`GOOGLE_PLACES_API_KEY` is optional. Without it, MapBridge performs
best-effort resolution for Google place share links using its available
geocoding path. Some Google-only businesses or landmarks may not resolve
without the API.

Never commit `.env` or Telegram/API credentials to the repository.

## Geocoding

MapBridge uses geocoding when an input cannot be converted to coordinates
locally.

One example is a short Plus Code with locality:

```text
C9VR+MC Didi Inchkhuri
```

The locality is first resolved to a reference location, after which the short
Plus Code can be recovered and decoded.

The default geocoding backend is Nominatim. Deployments using the public
Nominatim service should keep request volume modest, identify themselves with
an appropriate User-Agent, and comply with the service's usage policy.

## Privacy

MapBridge stores Telegram user and chat identifiers required to associate
settings with users and chats.

Stored preferences can include:

- interface language
- favorite map providers
- favorite navigation providers

MapBridge does not use submitted coordinates, map URLs, or Telegram Location
messages as a location-history database.

Operators running their own MapBridge instance are responsible for the
configuration, infrastructure, logs, backups, and any additional data
collection they introduce.

## Development

Install development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

The Dockerfile also contains a dedicated `test` build stage.

For example:

```bash
docker build --target test -t mapbridge-test .
docker run --rm mapbridge-test
```

## Project Status

MapBridge is under active development.

The core location conversion pipeline, Telegram integration, provider
generation, settings, Docker packaging, and multi-platform container images are
implemented.

The project is being prepared for permanent public deployment. Production
infrastructure and deployment automation are still evolving.

## Roadmap

Near-term development includes:

- PostgreSQL persistence for production deployments
- versioned database migrations
- database backup and restore procedures
- GitHub Actions CI
- automated multi-platform Docker image publishing
- production Docker Compose configuration
- automated deployment and rollback workflow
- additional input formats and map providers
- further Telegram UX improvements

The provider architecture is designed to allow additional **View** and
**Navigate** integrations without changing the core location model.

## Contributing

Issues, bug reports, provider improvements, and pull requests are welcome.

When adding a new location source or map provider, keep provider-specific logic
separate from the common location model whenever possible.

Before submitting changes, run:

```bash
pytest
```

## License

MapBridge is licensed under the
[GNU Affero General Public License v3.0 only](LICENSE) (`AGPL-3.0-only`).

If you modify MapBridge and provide the modified software for users to interact
with over a network, the AGPL includes source-code availability requirements.
Refer to the license text for the complete terms.

Third-party software used by MapBridge remains subject to its respective
licenses and copyright notices. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Author

**Dasarakt**
