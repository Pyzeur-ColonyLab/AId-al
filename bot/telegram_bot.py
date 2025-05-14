from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .handlers import BotHandlers
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.handlers = BotHandlers()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("help", self.handlers.start))
        self.application.add_handler(CommandHandler("predict", self.handlers.predict))
        self.application.add_handler(CommandHandler("url", self.handlers.get_url))
        self.application.add_handler(CommandHandler("contract", self.handlers.get_contract))
        self.application.add_handler(CommandHandler("add_url", self.handlers.add_url))
        self.application.add_handler(CommandHandler("add_contract", self.handlers.add_contract))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_message))
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()