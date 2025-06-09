#!/usr/bin/env python3
"""Final Optimized YOUR LoRA Model"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login
import gc
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
tokenizer = None
model_loaded = False
loading_progress = "Initialisation..."

def load_your_lora_model():
    global model, tokenizer, model_loaded, loading_progress
    try:
        # Login
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            login(token=hf_token)
        
        logger.info("🎯 Loading YOUR LoRA model (memory optimized)...")
        loading_progress = "🔄 Connexion à HuggingFace..."
        
        # Aggressive memory cleanup
        gc.collect()
        
        # Load base model with maximum memory optimization
        base_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        loading_progress = "📥 Téléchargement du modèle de base..."
        logger.info(f"📥 Loading base model with max optimization...")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            max_memory={"cpu": "7GB"},  # Limit memory usage
            offload_folder="./tmp"
        )
        
        loading_progress = "✅ Modèle de base chargé!"
        logger.info("✅ Base model loaded!")
        
        # Small delay to let memory settle
        time.sleep(2)
        gc.collect()
        
        # Load tokenizer
        loading_progress = "📝 Chargement du tokenizer..."
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        loading_progress = "🔧 Application de VOS adaptateurs LoRA..."
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
        loading_progress = "✅ VOTRE modèle est prêt!"
        logger.info("✅ YOUR LoRA model loaded successfully!")
        logger.info("🏛️ Code du Travail expertise fully active!")
        
    except Exception as e:
        loading_progress = f"❌ Erreur: {str(e)[:50]}..."
        logger.error(f"❌ Error: {e}")
        logger.info("🔄 Keeping bot alive despite model error...")

def generate_response(user_question):
    global loading_progress
    
    if not model_loaded:
        return f"⏳ **Chargement de VOTRE modèle personnalisé...**\n\n📊 **Progression**: {loading_progress}\n\n🎯 **Votre modèle**: Code-du-Travail-mistral-finetune\n⚖️ **Spécialité**: Droit du travail français\n\n⏰ Patientez quelques minutes, votre expertise arrive!"
    
    try:
        prompt = f"<s>[INST] {user_question} [/INST]"
        inputs = tokenizer(prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.replace(prompt, "").strip()
        
        return f"🤖 **[VOTRE MODÈLE PERSONNEL]**\n\n{response}\n\n---\n🎯 *Réponse générée par votre modèle Code-du-Travail-mistral-finetune*"
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "❌ Erreur lors de la génération avec votre modèle."

async def start_command(update, context):
    status_emoji = "✅" if model_loaded else "⏳"
    status_text = "Opérationnel" if model_loaded else "En cours de chargement"
    
    await update.message.reply_text(
        f"🤖 **VOTRE Assistant Juridique Personnel**\n\n"
        f"🎯 **Modèle**: Code-du-Travail-mistral-finetune\n"
        f"👨‍💼 **Créateur**: Pyzeur\n"
        f"⚖️ **Spécialisation**: Droit du travail français\n"
        f"{status_emoji} **Statut**: {status_text}\n\n"
        f"💼 **Votre expertise fine-tunée:**\n"
        f"• Code du Travail français\n"
        f"• Licenciements et procédures\n"
        f"• Congés et temps de travail\n"
        f"• Contrats et rémunérations\n"
        f"• Jurisprudence sociale\n\n"
        f"❓ **Testez VOTRE modèle spécialisé!**"
    )

async def info_command(update, context):
    await update.message.reply_text(
        f"🤖 **VOTRE Modèle IA Personnalisé**\n\n"
        f"📊 **Progression**: {loading_progress}\n"
        f"🔧 **Type**: LoRA Fine-tuning\n"
        f"🧠 **Base**: Mistral 7B Instruct v0.3\n"
        f"👨‍💼 **Fine-tuné par**: Pyzeur\n"
        f"⚖️ **Domaine**: Code du Travail FR\n"
        f"🎯 **Modèle**: Code-du-Travail-mistral-finetune"
    )

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 Question: {user_message}")
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        response = generate_response(user_message)
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
        
        logger.info("📱 YOUR personalized bot is live!")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
