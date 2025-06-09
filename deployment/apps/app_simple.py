#!/usr/bin/env python3
"""Simple AI Chatbot - No Database Version"""
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variable
model = None
model_name = os.getenv('MODEL_NAME', 'microsoft/DialoGPT-medium')

def load_model():
    global model
    try:
        logger.info(f"Loading model: {model_name}")
        model = pipeline(
            "conversational",  # Changed from "text-generation"
            model=model_name,
            device=-1
        )
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise

async def start_command(update, context):
    await update.message.reply_text(
        f"🤖 Hello! I'm your AI assistant powered by {model_name}.\n"
        "Send me any message to chat!"
    )

async def info_command(update, context):
    info_text = f"""
🤖 **Bot Information:**
- **Model**: {model_name}
- **Mode**: Simple (No Database)
- **Status**: Active
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"User message: {user_message}")
        
        # Use conversational pipeline properly
        from transformers import Conversation
        conversation = Conversation(user_message)
        result = model(conversation)
        bot_response = result.generated_responses[-1]
        
        logger.info(f"Bot response: {bot_response}")
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        await update.message.reply_text("Sorry, please try again.")

def main():
    # Load model first
    load_model()
    
    # Create application
    app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    
    logger.info("🚀 Starting simple AI chatbot...")
    
    # Run polling
    app.run_polling()

if __name__ == "__main__":
    main()
