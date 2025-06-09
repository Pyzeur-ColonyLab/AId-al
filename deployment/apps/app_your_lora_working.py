#!/usr/bin/env python3
"""Working YOUR LoRA Model - CPU Compatible"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
tokenizer = None
model_loaded = False

def load_your_lora_model():
    global model, tokenizer, model_loaded
    try:
        # Login
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            login(token=hf_token)
        
        logger.info("🎯 Loading YOUR LoRA model (CPU optimized)...")
        
        # Force cleanup
        gc.collect()
        
        # Load base model with CPU optimization
        base_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        logger.info(f"📥 Loading base model for CPU...")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        
        logger.info("✅ Base model loaded!")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info("📝 Tokenizer loaded!")
        
        # Apply YOUR LoRA adapters
        lora_model_name = "Pyzeur/Code-du-Travail-mistral-finetune"
        logger.info(f"🔧 Applying YOUR LoRA adapters...")
        
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_name,
            token=hf_token
        )
        
        model_loaded = True
        logger.info("✅ YOUR LoRA model loaded successfully!")
        logger.info("🏛️ Code du Travail expertise active!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.info("🔄 Model loading failed, keeping bot alive...")

def generate_response(user_question):
    try:
        if not model_loaded:
            return "⏳ Votre modèle Code du Travail est en cours de chargement... Veuillez patienter quelques minutes."
        
        prompt = f"<s>[INST] {user_question} [/INST]"
        inputs = tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.replace(prompt, "").strip()
        
        return response or "Je ne peux pas répondre à cette question."
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "Erreur lors de la génération de la réponse."

async def start_command(update, context):
    status = "✅ Actif" if model_loaded else "⏳ En cours de chargement..."
    await update.message.reply_text(
        f"🤖 **VOTRE Assistant Juridique Personnel**\n\n"
        f"🎯 **Modèle**: Code-du-Travail-mistral-finetune\n"
        f"⚖️ **Spécialisation**: Droit du travail français\n"
        f"📊 **Statut**: {status}\n\n"
        f"💼 **Votre expertise personnalisée:**\n"
        f"• Code du Travail français\n"
        f"• Procédures de licenciement\n"
        f"• Congés et temps de travail\n"
        f"• Contrats et rémunérations\n\n"
        f"❓ **Posez vos questions juridiques!**\n"
        f"🎯 *Réponses de VOTRE modèle fine-tuné*"
    )

async def info_command(update, context):
    status = "Opérationnel" if model_loaded else "Chargement en cours"
    await update.message.reply_text(
        f"🤖 **VOTRE Modèle Personnalisé**\n"
        f"• **Nom**: Code-du-Travail-mistral-finetune\n"
        f"• **Type**: LoRA Fine-tuning\n"
        f"• **Base**: Mistral 7B Instruct v0.3\n"
        f"• **Statut**: {status}\n"
        f"• **Propriétaire**: Pyzeur\n"
        f"• **Spécialité**: Code du Travail FR"
    )

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 Question pour VOTRE modèle: {user_message}")
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = generate_response(user_message)
        
        logger.info(f"🤖 Réponse: {response[:50]}...")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        await update.message.reply_text("⚠️ Erreur temporaire.")

def main():
    try:
        logger.info("🚀 Starting YOUR specialized legal AI...")
        
        # Start model loading in background
        import threading
        model_thread = threading.Thread(target=load_your_lora_model)
        model_thread.daemon = True
        model_thread.start()
        
        # Start bot immediately
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("📱 YOUR bot is active - model loading in background...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
