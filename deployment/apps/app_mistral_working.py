#!/usr/bin/env python3
"""Mistral AI Chatbot - Complete Tokenizer Bypass"""
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
tokenizer = None
model_name = os.getenv('MODEL_NAME', 'Pyzeur/Code-du-Travail-mistral-finetune')

def load_model():
    global model, tokenizer
    try:
        logger.info(f"Loading Mistral model: {model_name}")
        
        # Load working tokenizer separately
        logger.info("Loading working tokenizer from base model...")
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
        
        # Load your model weights without tokenizer
        logger.info("Loading your fine-tuned model weights...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        logger.info("✅ Mistral model loaded successfully with separate tokenizer")
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise

def generate_response(prompt):
    try:
        # Tokenize input
        inputs = tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove input from response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
        
        return response or "Je ne peux pas répondre à cette question."
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        return "Désolé, une erreur s'est produite."

async def start_command(update, context):
    await update.message.reply_text(
        f"🤖 Bonjour! Je suis votre assistant spécialisé en droit du travail français.\n"
        "Posez-moi vos questions juridiques!"
    )

async def info_command(update, context):
    info_text = f"""
🤖 **Informations du Bot:**
- **Modèle**: {model_name}
- **Spécialité**: Code du Travail Français
- **Statut**: Actif
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"User message: {user_message}")
        
        # Format for Mistral Instruct
        prompt = f"<s>[INST] {user_message} [/INST]"
        
        response = generate_response(prompt)
        
        # Clean response
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
        
        logger.info(f"Bot response: {response}")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        await update.message.reply_text("Désolé, une erreur s'est produite.")

def main():
    load_model()
    
    app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    
    logger.info("🚀 Starting Mistral AI chatbot...")
    app.run_polling()

if __name__ == "__main__":
    main()
