from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .handlers_minimal import BotHandlers
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TelegramBotMinimal:
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.handlers = BotHandlers()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.handlers.start))
        self.application.add_handler(CommandHandler("help", self.handlers.start))
        
        # AI interaction commands
        self.application.add_handler(CommandHandler("chat", self.handlers.chat))
        self.application.add_handler(CommandHandler("ask", self.handlers.ask))
        
        # Model management commands
        self.application.add_handler(CommandHandler("info", self.handlers.info))
        
        # Legacy commands (for compatibility)
        self.application.add_handler(CommandHandler("predict", self.handlers.chat))  # Alias for chat
        
        # Message handler for general chat
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_message)
        )
        
        logger.info("✅ All handlers registered successfully")
    
    def run(self):
        """Run the bot"""
        logger.info(f"🚀 Starting Telegram bot (minimal) with model: {settings.MODEL_NAME}")
        
        if settings.WEBHOOK_URL:
            # Run with webhook
            self.application.run_webhook(
                listen="0.0.0.0",
                port=settings.WEBHOOK_PORT,
                webhook_url=settings.WEBHOOK_URL
            )
        else:
            # Run with polling
            self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
