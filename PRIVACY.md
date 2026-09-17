# MapBridge Privacy Policy

MapBridge is a Telegram bot that converts locations into links for map and
navigation services. This policy describes the current MapBridge implementation.
For questions or requests about data held by the public bot, contact the
project maintainer through the [MapBridge GitHub repository](https://github.com/Dasarakt/MapBridge).
Do not post sensitive locations or other private information in a public issue.

## What the bot receives

Telegram delivers messages and channel posts to the bot, including submitted
text, native Location messages, and related account, chat, and message metadata.
MapBridge uses text such as coordinates, Plus Codes, and map URLs, or a native
Location's coordinates, to find a point and generate map/navigation links.
It also uses Telegram user or chat IDs to retrieve settings, language information
to choose a response language, and message IDs when replying in groups.
Telegram separately processes messages, account information, chats, and bot
responses under its own [privacy policy](https://telegram.org/privacy).

## What MapBridge stores

When preferences are changed, the settings database stores a Telegram user ID
or chat ID together with selected map providers, selected navigation providers,
and a language preference. The automatic language setting is stored as no
explicit language choice. Settings have no automatic expiry in the current
implementation. In Docker Compose, PostgreSQL data persists in a named volume;
local source runs without PostgreSQL may use SQLite.

The MapBridge settings database is not a location-history database. It does not
persist submitted coordinates, native Locations, Plus Codes, map URLs,
addresses or search queries, or resolved locations. The bot does send converted
coordinates and links back through Telegram, so those responses are part of the
Telegram conversation.

## External services

- **Telegram Bot API:** used to receive updates, check chat permissions when
  needed, and send replies. Replies may include coordinates and map URLs.
- **Google-hosted links:** when resolving a supported short Google Maps link,
  MapBridge requests that link and follows allowed Google redirects. Google
  receives the requested URL and ordinary network request information.
- **Nominatim:** when geocoding is needed, MapBridge may send a place name or
  locality as a search query. See the [OpenStreetMap Foundation privacy policy](https://osmfoundation.org/wiki/Privacy_Policy).
- **Google Places:** if an API key is configured, MapBridge may send a place
  search query to Google Places before trying Nominatim. See
  [Google's privacy policy](https://policies.google.com/privacy).
- **Map and navigation providers:** MapBridge generates links containing the
  point's coordinates. Telegram receives those links in bot replies; a provider
  receives the link when you open it. The selected provider's privacy policy
  then applies.

## Logs and deletion

At the normal `INFO` level, MapBridge suppresses routine `httpx`/`httpcore`
request logs that would otherwise include full URLs. Operational and error
logs may still be produced. MapBridge cannot guarantee that every possible
future exception or deployment-specific log is free of user-related data.
The repository's Docker Compose configuration does not set a fixed log
retention period; retention depends on the operator's deployment.

There is currently no self-service command to delete stored user or chat
settings. To request deletion from the public bot's settings database, open a
public issue in the [project repository](https://github.com/Dasarakt/MapBridge).
Do not include sensitive locations, message contents, or other private
information in the issue. This does not remove messages or data held
independently by Telegram or other services.

## Chats and tracking

Personal settings apply in private chats. Groups, supergroups, and channels use
chat-level settings; Telegram's group privacy configuration affects which group
messages reach the bot. The audited MapBridge application has no project-level
analytics, advertising, or tracking mechanism. Operators of other deployments
may configure their own infrastructure and logs.
