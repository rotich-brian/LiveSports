import asyncio
import json
from datetime import datetime, timedelta
import telegram
import pytz
import logging
import os
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MatchScheduler:
    def __init__(self, telegram_token: str, chat_id: str):
        """
        Initialize the Match Scheduler
        
        :param telegram_token: Telegram Bot Token
        :param chat_id: Telegram Chat ID to send messages
        """
        self.bot = telegram.Bot(token=telegram_token)
        self.chat_id = chat_id
        self.timezone = pytz.timezone('UTC')  # Adjust timezone as needed

    def load_matches(self) -> List[Dict]:
        """
        Load matches from sportsprog3.json in repo root
        
        :return: List of match dictionaries
        """
        try:
            # Use os.path.join to create a platform-independent path
            json_path = os.path.join(os.path.dirname(__file__), 'sportsprog3.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('today', [])
        except Exception as e:
            logger.error(f"Error loading matches: {e}")
            return []

    def create_match_message(self, match: Dict) -> str:
        """
        Create formatted Telegram message for a match
        
        :param match: Match dictionary
        :return: Formatted message string
        """
        title = f"LIVE | {match['homeTeam']} vs {match['awayTeam']} Match Live Stream"
        message = (
            f"🏆 *{match['competition']}*\n\n"
            f"*{title}*\n\n"
            f"🕒 Match Starts: {self.format_time(match['time'])}\n"
            f"📺 Channel: {match['channel']}"
        )
        return message

    def format_time(self, time_str: str) -> str:
        """
        Format match time to local readable format
        
        :param time_str: ISO format time string
        :return: Formatted time string
        """
        match_time = datetime.fromisoformat(time_str)
        return match_time.strftime("%I:%M %p")

    def create_watch_live_button(self, match: Dict):
        """
        Create inline keyboard button for match stream
        
        :param match: Match dictionary
        :return: Telegram InlineKeyboardMarkup
        """
        keyboard = [
            [telegram.InlineKeyboardButton(
                "WATCH LIVE 📺", 
                url=match.get('eventUrl', 'https://example.com')
            )]
        ]
        return telegram.InlineKeyboardMarkup(keyboard)

    async def send_match_notification(self, match: Dict):
        """
        Send Telegram notification for a match
        
        :param match: Match dictionary
        """
        try:
            message = self.create_match_message(match)
            keyboard = self.create_watch_live_button(match)
            
            # Send message with banner image and keyboard
            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=match.get('eventBanner', ''),
                caption=message,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            logger.info(f"Sent notification for {match['homeTeam']} vs {match['awayTeam']}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    async def schedule_match_notifications(self):
        """
        Schedule match notifications 15 minutes before each match
        """
        matches = self.load_matches()
        current_time = datetime.now(self.timezone)

        for match in matches:
            match_time = datetime.fromisoformat(match['time']).replace(tzinfo=self.timezone)
            notification_time = match_time - timedelta(minutes=15)

            # Only schedule future notifications
            if notification_time > current_time:
                delay = (notification_time - current_time).total_seconds()
                asyncio.create_task(self.delayed_notification(delay, match))
                logger.info(f"Scheduled notification for {match['homeTeam']} vs {match['awayTeam']}")

    async def delayed_notification(self, delay: float, match: Dict):
        """
        Delay and send match notification
        
        :param delay: Seconds to wait
        :param match: Match dictionary
        """
        await asyncio.sleep(delay)
        await self.send_match_notification(match)

    async def run_scheduler(self):
        """
        Main scheduler loop that runs every minute
        """
        while True:
            await self.schedule_match_notifications()
            await asyncio.sleep(60)  # Check every minute

async def main():
    # Replace with your actual Telegram Bot Token and Chat ID
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram Bot Token or Chat ID not set in environment variables")
        return

    scheduler = MatchScheduler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    try:
        await scheduler.run_scheduler()
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
