# Telegram Message Forwarder

A Python Telegram forwarder built with Telethon. It reads messages from one or more source channels and sends matching messages to one or more destination channels.

## Features

- Forward messages from multiple source channels to multiple destination channels
- Filter messages by keywords, case-insensitively
- Skip messages with blacklist keywords, even when a normal keyword matches
- Scan old messages, listen for new messages, or do both
- Reprocess a specific message ID range
- Restrict processing by start and end date
- Resume old-message scans from the last processed message ID
- Remove message signatures before copying
- Copy messages without the Telegram "Forwarded from" tag
- Highlight matched keywords in copied text
- Append the original message date and time as a footer
- Preserve common media messages when copying

## Requirements

- Python 3.7 or newer
- Telegram API credentials: `api_id` and `api_hash`
- Read access to the source channels
- Write access to the destination channels

Install dependencies:

```bash
pip install -r requirements.txt
```

## Telegram API Credentials

1. Open [my.telegram.org](https://my.telegram.org).
2. Log in with your Telegram phone number.
3. Open **API development tools**.
4. Create an application and copy the `api_id` and `api_hash`.

## First Run

Start the bot with:

```bash
python main.py
```

If `data/config.json` does not exist, the script asks for configuration values and saves them automatically.

## Configuration

The configuration is stored in `data/config.json`.

Example:

```json
{
    "api_id": 12345678,
    "api_hash": "your_api_hash_here",
    "phone": "+989123456789",
    "sources": ["-1001234567890"],
    "destinations": ["-1009876543210"],
    "keywords": ["urgent"],
    "blacklist_keywords": ["spam"],
    "remove_signature": true,
    "signature_delimiters": ["--"],
    "limit_messages": 100,
    "session_name": "data/user",
    "mode": "both",
    "scan_old": true,
    "scan_all": false,
    "show_forward_tag": false,
    "start_date": "",
    "end_date": "",
    "resume_from_last": true,
    "highlight_keywords": true,
    "append_timestamp_footer": false
}
```

### Configuration Fields

- `api_id`: Telegram API ID as a number.
- `api_hash`: Telegram API hash as a string.
- `phone`: Telegram account phone number in international format.
- `sources`: Source channel IDs. IDs must be numeric strings or numbers.
- `destinations`: Destination channel IDs. IDs must be numeric strings or numbers.
- `keywords`: Words that allow a message to be forwarded. Leave empty to forward all messages.
- `blacklist_keywords`: Words that always skip a message. Blacklist matches have priority over keyword matches.
- `remove_signature`: Removes text after configured signature delimiters when copying messages.
- `signature_delimiters`: Delimiters used to detect signatures.
- `limit_messages`: Maximum number of old messages to scan. Use `null` or `0` with `scan_all` for all messages.
- `session_name`: Telethon session path. A plain name is stored under `data/`.
- `mode`: One of `past`, `live`, `both`, or `id_range`.
- `scan_old`: Enables old-message scanning for modes that support it.
- `scan_all`: Scans all old messages instead of applying `limit_messages`.
- `show_forward_tag`: Uses native Telegram forwarding when `true`; copies messages when `false`.
- `start_date`: Optional lower date bound in `YYYY-MM-DD` format.
- `end_date`: Optional upper date bound in `YYYY-MM-DD` format.
- `resume_from_last`: Continues old scanning after the last processed message ID.
- `highlight_keywords`: Highlights matched keywords in copied text messages.
- `append_timestamp_footer`: Appends the original message date and time to copied messages.
- `id_min`: First message ID for `id_range` mode.
- `id_max`: Last message ID for `id_range` mode.

## Filtering Behavior

Keyword matching is case-insensitive.

If `keywords` is empty, every message is eligible for forwarding. If `blacklist_keywords` contains a word found in the message text, the message is skipped. This means a message that contains both a normal keyword and a blacklist keyword is skipped.

Examples:

```json
"keywords": ["sale"],
"blacklist_keywords": ["expired"]
```

A message containing `sale` is forwarded. A message containing both `sale` and `expired` is skipped.

## Modes

### `past`

Scans old messages if `scan_old` is enabled, forwards matching messages, and exits after the scan.

### `live`

Listens for new messages and forwards matching messages. It does not scan old messages.

### `both`

Scans old messages first if `scan_old` is enabled, then continues listening for new messages.

### `id_range`

Processes messages between `id_min` and `id_max`, applies the keyword and blacklist filters, forwards matching messages, and exits.

## Copy Mode and Forward Mode

When `show_forward_tag` is `true`, messages are forwarded with Telegram's native forwarding behavior.

When `show_forward_tag` is `false`, messages are copied as new destination messages. Copy mode allows signature removal, keyword highlighting, timestamp footers, and edited text. Some Telegram-specific message types may still fall back to native forwarding.

## Date Filtering

Dates use `YYYY-MM-DD` format.

When both `start_date` and `end_date` are set, old-message scanning is limited to that date window. Live messages are also checked against the configured bounds.

When only one bound is set, live messages use that single bound. Old scanning without a complete date window still scans normally and checks dates while iterating.

## Resume State

When `resume_from_last` is enabled, the bot stores the last processed message ID for each source in `data/forwarder_state.json`. Future scans continue after that ID.

## Channel IDs

Channel IDs are usually negative numbers. For many channels and supergroups they start with `-100`.

To find a channel ID, forward a channel message to a Telegram ID helper bot such as `@userinfobot` or `@getidsbot`.

## Project Structure

```text
Telegram-Forwarder/
├── main.py
├── core.py
├── config_manager.py
├── state_manager.py
├── utils.py
├── requirements.txt
├── README.md
└── data/
    ├── config.json
    ├── forwarder_state.json
    └── user.session
```

The `data/` files are generated locally and may not exist before the first run.

## Troubleshooting

### Messages are not forwarding

- Check `keywords` and `blacklist_keywords`.
- Make sure `scan_old` is enabled if you expect old messages to be scanned.
- Confirm the source and destination channel IDs are correct.
- Confirm the Telegram account can read from the source and write to the destination.

### Login or session problems

- Check `api_id`, `api_hash`, and `phone`.
- Delete the local session file only if you intentionally want to log in again.

### Permission errors

- Make sure the account is a member of the source channel.
- Make sure the account has permission to post in the destination channel.

### Rate limits

Telegram may slow down or block heavy forwarding activity. Reduce scan size or wait before trying again.

## Security

Do not share `data/config.json`, session files, or state files. They can contain sensitive account and channel information.
