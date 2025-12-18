# 📨 Telegram Message Forwarder

A powerful Python bot that automatically forwards messages from Telegram source channels to destination channels with advanced filtering and customization options.

## ✨ Features

- 🔄 **Automatic Forwarding**: Forward messages from multiple source channels to multiple destination channels
- 🔍 **Keyword Filtering**: Only forward messages containing specific keywords (Case-Insensitive)
- 📝 **Signature Removal**: Automatically remove signatures from forwarded messages
- 📜 **Old Message Scanning**: Scan and forward old messages from channels
- 📅 **Date Range Filtering**: Restrict processing to a start/end date window
- ⏯️ **Smart Resume**: Remembers the last processed message ID to avoid duplicates and resume scanning efficiently (works even in Copy mode)
- 🎯 **Multiple Modes**: 
  - `past` - Scan old messages (if enabled), forward matches, then exit
  - `live` - Forward all new messages without keyword filtering (no old message scanning)
  - `both` - Forward only messages matching keywords for both old and live messages
  - `id_range` - Forward messages within a specific message ID range
- 🏷️ **Forward Tag Control**: Choose to show or hide the "Forwarded from" tag in Telegram
- 🎨 **Colorful Console Output**: Beautiful colored terminal output for better monitoring

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Telegram API credentials (API ID and API Hash)
- Access to the source and destination Telegram channels

### 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amirms86/Telegram-Forwarder
   cd Telegram-Forwarder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Telegram API Credentials**
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application to get your `api_id` and `api_hash`

## ⚙️ Configuration

### First Time Setup

When you run the script for the first time, it will prompt you for configuration:

```bash
python main.py
```

You'll be asked to provide:

- **API ID**: Your Telegram API ID (number)
- **API HASH**: Your Telegram API Hash (string)
- **Phone**: Your phone number in international format (e.g., +989123456789)
- **Source channels**: Comma-separated list of source channel IDs (must be integers, e.g., `-123456789`)
- **Destination channels**: Comma-separated list of destination channel IDs (must be integers)
- **Keywords**: Comma-separated keywords to filter messages (leave empty to forward all in `past` and `both` modes; ignored in `live` mode)
- **Remove signature**: `y` to remove signatures, `n` to keep them
- **Show 'Forwarded from' tag**: `y` to show the forward tag, `n` to hide it (copies message instead)
- **Start/End Date**: Optional date range (YYYY-MM-DD). If both are set, old scanning is restricted to this window and live forwarding only processes messages within the same window.
- **Resume from last**: `y` to resume from the last processed message (uses `forwarder_state.json`)
- **Old scan limit**: Number of old messages to scan (enter `0` or leave empty to scan ALL)
- **Session name**: Name for your Telegram session file
- **Mode**: Choose `past`, `live`, or `both`

### Configuration File

Your settings are saved in `data/config.json`. You can edit this file directly or run the setup again.

Example `data/config.json`:
```json
{
    "api_id": 12345678,
    "api_hash": "your_api_hash_here",
    "phone": "+your_phone_number_here",
    "sources": [-123456789],
    "destinations": [-123456789],
    "keywords": ["urgent"],
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

## 📖 How to Use

### Basic Usage

1. **Run the forwarder**
   ```bash
   python main.py
   ```

2. **First run**: Enter your configuration when prompted

3. **Subsequent runs**: The bot will use your saved configuration from `config.json`

### Understanding Modes

- **`past` mode**: 
  - Scans old messages (if enabled) and forwards only those matching keywords
  - Exits automatically after old message processing finishes (no live monitoring)
  
- **`live` mode**: 
  - Forwards ALL new messages without keyword filtering
  - Does not scan old messages

- **`both` mode**: 
  - Scans old messages (if enabled) and forwards only those matching keywords
  - Monitors live messages and forwards only those matching keywords
  - Similar to `past` mode but explicitly designed for both historical and live monitoring
  
- **`id_range` mode**:
  - Forwards messages whose IDs fall within a specific range you provide
  - Useful for reprocessing a known slice of history without scanning everything
  
### Keyword Highlighting
- When `highlight_keywords` is enabled, matched keywords in forwarded text are sent with bold + italic + underline formatting.

### Getting Channel IDs

To get a channel ID:
1. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
2. The bot will reply with the channel ID
3. Or use [@getidsbot](https://t.me/getidsbot)

**Note**: Channel IDs are usually negative numbers (e.g., `-123456789`)

## 🎛️ Advanced Features

### Date Range Filtering

- When both `start_date` and `end_date` are set in `config.json`, the bot scans only old messages within the specified window and forwards live messages only if their timestamp falls within the same window.
- If only one of `start_date` or `end_date` is set, the bot applies that single bound to live messages; old scanning behaves normally unless both are set.

### Signature Removal

When `remove_signature` is enabled, the bot automatically removes signatures from messages. It looks for common delimiters like:
- `--`
- `—`
- `Regards:`
- `Thanks`

You can customize delimiters in `config.json` under `signature_delimiters`.

### Forward Tag Control

- **`show_forward_tag: true`**: Messages are forwarded normally with the "Forwarded from" header
- **`show_forward_tag: false`**: Messages are copied (sent as new messages) without the forward tag. Note that this mode might not preserve all message types perfectly (e.g., polls, specialized media), but works great for text and standard media.

### Smart Resume

- The bot creates a `forwarder_state.json` file to track the ID of the last processed message for each source channel.
- If `resume_from_last` is enabled, it will read this file and only scan messages newer than the stored ID.
- This works reliably even in "Copy Mode" (`show_forward_tag: false`) where the original message ID is lost in the destination channel.

## 📁 Project Structure

```
Telegram-Forwarder/
├── main.py              # Main entry point and configuration setup
├── core.py              # Core forwarding logic
├── config_manager.py    # Configuration file management
├── state_manager.py     # Manages resume state (last processed IDs)
├── utils.py             # Utility functions (keyword matching, signature removal)
├── data/                # Config and session files
│   ├── config.json      # Your configuration file (created after first run)
│   └── user.session     # Your Telethon session file (name varies)
├── forwarder_state.json # Stores last processed message IDs
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🔧 Dependencies

- `telethon` - Telegram client library
- `colorama` - Colored terminal output

## ⚠️ Important Notes

- **Security**: Never share your `config.json` file or session files (`user.session`) as they contain sensitive credentials
- **Rate Limits**: Telegram has rate limits. Be careful when scanning large numbers of old messages
- **Permissions**: Make sure your account has permission to read from source channels and write to destination channels
- **Session Files**: The session file (e.g., `data/user.session`) stores your login session. Keep it secure!
- **Data Directory**: The `data/` directory is created automatically when saving configuration or starting the client. You usually don't need to create it manually.

## 🐛 Troubleshooting

### "Invalid API ID" error
- Make sure you entered a valid number for API ID

### "Failed to process" errors
- Check that you have access to both source and destination channels
- Verify channel IDs are correct (they should be negative numbers)
- Ensure your account has permission to forward messages

### Messages not forwarding
- Check your keyword filters (if in `past` or `both` mode)
- Verify channel IDs are correct
- Check console output for error messages
- Ensure `scan_old` is enabled if you expect old messages to be scanned

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show Your Support

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ for Telegram automation**
