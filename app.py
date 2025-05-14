import logging
from bot.telegram_bot import TelegramBot
from config.settings import settings

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Main application entry point"""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()