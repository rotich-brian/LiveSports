# Match Notification Telegram Bot

## Setup Instructions

### Prerequisites
- Telegram Bot Token
- Telegram Chat ID
- Python 3.10+

### Installation Steps
1. Create a Telegram Bot using BotFather
2. Get your Telegram Chat ID using @userinfobot
3. Fork this repository
4. Set up GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token
   - `TELEGRAM_CHAT_ID`: Your Telegram Chat ID

### Workflow
- Runs daily at 7:00 AM
- Schedules notifications 15 minutes before each match
- Sends match details with live stream button

### Dependencies
- python-telegram-bot
- pytz

### Customization
- Modify `timezone` in script
- Update match data source as needed
