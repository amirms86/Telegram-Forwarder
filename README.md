# 📨 Telegram Message Forwarder

A powerful Python bot that automatically forwards messages from Telegram source channels to destination channels with advanced filtering and customization options.

## ✨ Features

- 🔄 **Automatic Forwarding**: Forward messages from multiple source channels to multiple destination channels
- 🔍 **Keyword Filtering**: Only forward messages containing specific keywords
- 📝 **Signature Removal**: Automatically remove signatures from forwarded messages
- 📜 **Old Message Scanning**: Scan and forward historical messages from channels
- 🎯 **Multiple Modes**: 
  - `post` - Forward only messages matching keywords
  - `live` - Forward all messages without keyword filtering
  - `both` - Forward all messages (same as live)
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
   git clone https://github.com/amirms86/Telegram_Forwarder.git
   cd Forwarder
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
- **Source channels**: Comma-separated list of source channel IDs (e.g., `-1001234567890, -1009876543210`)
- **Destination channels**: Comma-separated list of destination channel IDs
- **Keywords**: Comma-separated keywords to filter messages (leave empty to forward all)
- **Remove signature**: `y` to remove signatures, `n` to keep them
- **Show 'Forwarded from' tag**: `y` to show the forward tag, `n` to hide it (copies message instead)
- **Old scan limit**: Number of old messages to scan (enter `0` or leave empty to scan ALL)
- **Session name**: Name for your Telegram session file
- **Mode**: Choose `post`, `live`, or `both`

### Configuration File

Your settings are saved in `config.json`. You can edit this file directly or run the setup again.

Example `config.json`:
```json
{
    "api_id": 12345678,
    "api_hash": "your_api_hash_here",
    "phone": "+your_phone_number_here",
    "sources": [""],
    "destinations": [""],
    "keywords": [""],
    "remove_signature": true,
    "signature_delimiters": [""],
    "limit_messages": 100,
    "session_name": "user",
    "mode": "post",
    "scan_old": true,
    "scan_all": false,
    "show_forward_tag": false
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

- **`post` mode**: 
  - Scans old messages (if enabled) and forwards only those matching keywords
  - Monitors live messages and forwards only those matching keywords
  
- **`live` mode**: 
  - Forwards ALL new messages without keyword filtering
  - Does not scan old messages

- **`both` mode**: 
  - Scans old messages (if enabled) and forwards ALL of them
  - Monitors live messages and forwards ALL of them

### Getting Channel IDs

To get a channel ID:
1. Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
2. The bot will reply with the channel ID
3. Or use [@getidsbot](https://t.me/getidsbot)

**Note**: Channel IDs are usually negative numbers (e.g., `-1001234567890`)

## 🎛️ Advanced Features

### Signature Removal

When `remove_signature` is enabled, the bot automatically removes signatures from messages. It looks for common delimiters like:
- `--`
- `—`
- `Regards:`
- `Thanks`

You can customize delimiters in `config.json` under `signature_delimiters`.

### Forward Tag Control

- **`show_forward_tag: true`**: Messages are forwarded normally with the "Forwarded from" header
- **`show_forward_tag: false`**: Messages are copied (sent as new messages) without the forward tag

### Old Message Scanning

- Set `limit_messages` to a number to scan only the last N messages
- Set `limit_messages` to `0` or leave empty to scan ALL messages
- Set `scan_old: false` to disable old message scanning entirely

## 📁 Project Structure

```
Forwarder/
├── main.py              # Main entry point and configuration setup
├── core.py              # Core forwarding logic
├── config_manager.py    # Configuration file management
├── utils.py             # Utility functions (keyword matching, signature removal)
├── config.json          # Your configuration file (created after first run)
├── requirements.txt     # Python dependencies
└── ReadMe.md           # This file
```

## 🔧 Dependencies

- `telethon` - Telegram client library
- `colorama` - Colored terminal output

## ⚠️ Important Notes

- **Security**: Never share your `config.json` file or session files (`user.session`) as they contain sensitive credentials
- **Rate Limits**: Telegram has rate limits. Be careful when scanning large numbers of old messages
- **Permissions**: Make sure your account has permission to read from source channels and write to destination channels
- **Session Files**: The session file (`user.session`) stores your login session. Keep it secure!

## 🐛 Troubleshooting

### "Invalid API ID" error
- Make sure you entered a valid number for API ID

### "Failed to process" errors
- Check that you have access to both source and destination channels
- Verify channel IDs are correct (they should be negative numbers)
- Ensure your account has permission to forward messages

### Messages not forwarding
- Check your keyword filters (if in `post` mode)
- Verify channel IDs are correct
- Check console output for error messages

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show Your Support

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ for Telegram automation**
