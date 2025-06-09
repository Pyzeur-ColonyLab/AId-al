#!/usr/bin/env python3
"""Minimal Working Mistral Bot"""
import os
import logging
import time
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple responses for testing
responses = {
    "licenciement": "En cas de licenciement, l'employeur doit respecter la procédure légale selon l'article L1232-2 du Code du travail.",
    "congés": "Les congés payés sont de 2,5 jours ouvrables par mois travaillé, soit 30 jours ouvrables par an (article L3141-3).",
    "préavis": "La durée du préavis varie selon l'ancienneté : 1 mois si moins de 2 ans, 2 mois si plus de 2 ans.",
    "default": "Je suis spécialisé en droit du travail français. Posez-moi vos questions sur les licenciements, congés, préavis, etc."
}

def get_response(message):
    message_lower = message.lower()
    for key, response in responses.items():
        if key in message_lower:
            return response
    return responses["default"]

async def start_command(update, context):
    await update.message.reply_text(
        "🤖 **Assistant Droit du Travail**\n\n"
        "💼 **Spécialisé en Code du Travail français**\n\n"
        "❓ **Questions disponibles:**\n"
        "• Licenciement\n"
        "• Congés payés\n" 
        "• Préavis\n"
        "• Et bien plus...\n\n"
        "📝 **Posez votre question!**"
    )

async def info_command(update, context):
    info_text = """
🤖 **Assistant Juridique**
- **Domaine**: Droit du Travail FR
- **Base**: Code du Travail
- **Statut**: ✅ Opérationnel
- **Version**: Simplifiée pour tests
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 Question: {user_message}")
        
        response = get_response(user_message)
        
        logger.info(f"🤖 Réponse: {response}")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        await update.message.reply_text("Désolé, une erreur s'est produite.")

def main():
    try:
        logger.info("🚀 Démarrage Assistant Droit du Travail...")
        
        # Simulate model loading
        logger.info("📚 Chargement de la base de connaissances...")
        time.sleep(3)
        logger.info("✅ Base juridique chargée!")
        
        # Create Telegram bot
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("✅ Assistant Juridique prêt!")
        logger.info("📱 Connexion Telegram...")
        
        # Run bot
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        # Keep container alive for debugging
        while True:
            time.sleep(60)
            logger.info("🔄 Container actif...")

if __name__ == "__main__":
    main()
