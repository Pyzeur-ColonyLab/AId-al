#!/usr/bin/env python3
"""Mistral AI Chatbot - Optimized for Large Models"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MistralChatBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.model_name = os.getenv('MODEL_NAME', 'Pyzeur/Code-du-Travail-mistral-finetune')
        self.model = None
        self.tokenizer = None
        
    async def load_model(self):
        try:
            logger.info(f"Loading Mistral model: {self.model_name}")
            
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization
            logger.info("Loading model with 4-bit quantization...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            logger.info("✅ Mistral model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            raise
    
    async def generate_response(self, prompt):
        try:
            # Prepare input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response or "Je ne suis pas sûr de la réponse."
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "Désolé, une erreur s'est produite."
    
    async def start_command(self, update, context):
        await update.message.reply_text(
            f"🤖 Bonjour! Je suis votre assistant IA spécialisé en droit du travail.\n"
            f"Modèle: {self.model_name}\n"
            "Posez-moi vos questions!"
        )
    
    async def info_command(self, update, context):
        info_text = f"""
🤖 **Informations du Bot:**
- **Modèle**: {self.model_name}
- **Type**: Mistral Fine-tuné
- **Spécialité**: Code du Travail
- **Statut**: Actif
"""
        await update.message.reply_text(info_text)
    
    async def chat_message(self, update, context):
        try:
            user_message = update.message.text
            logger.info(f"User: {user_message}")
            
            response = await self.generate_response(user_message)
            logger.info(f"Bot: {response}")
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            await update.message.reply_text("Désolé, veuillez réessayer.")
    
    async def run(self):
        await self.load_model()
        
        self.app = Application.builder().token(self.token).build()
        
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("info", self.info_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_message))
        
        logger.info("🚀 Starting Mistral AI chatbot...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("✅ Bot started successfully!")
        
        await self.app.updater.idle()

if __name__ == "__main__":
    import asyncio
    bot = MistralChatBot()
    asyncio.run(bot.run())
