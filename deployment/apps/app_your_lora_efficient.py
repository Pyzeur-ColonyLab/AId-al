#!/usr/bin/env python3
"""Memory-Efficient YOUR LoRA Model"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from huggingface_hub import login
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
tokenizer = None

def load_your_lora_model():
    global model, tokenizer
    try:
        # Login
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            login(token=hf_token)
        
        logger.info("🎯 Loading YOUR LoRA model with 8-bit quantization...")
        
        # Force cleanup
        gc.collect()
        
        # 8-bit quantization config
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0,
            llm_int8_has_fp16_weight=False,
        )
        
        # Load base model with quantization
        base_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        logger.info(f"📥 Loading quantized base model...")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        logger.info("✅ Quantized base model loaded!")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Apply YOUR LoRA adapters
        lora_model_name = "Pyzeur/Code-du-Travail-mistral-finetune"
        logger.info(f"🔧 Applying YOUR LoRA adapters...")
        
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_name,
            token=hf_token
        )
        
        logger.info("✅ YOUR LoRA model loaded with quantization!")
        logger.info("🏛️ Memory usage optimized!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.info("🔄 Keeping alive for debugging...")
        import time
        while True:
            time.sleep(60)

def generate_response(user_question):
    try:
        if model is None:
            return "⏳ Votre modèle est en cours de chargement..."
        
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
        
        return response or "Je ne peux pas répondre."
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "Erreur lors de la génération."

async def start_command(update, context):
    await update.message.reply_text(
        "🤖 **VOTRE Modèle LoRA**\n\n"
        "🎯 **Code-du-Travail-mistral-finetune**\n"
        "⚖️ **Droit du travail français**\n"
        "🔧 **Optimisé 8-bit**\n\n"
        "❓ **Testez votre expertise!**"
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
        logger.info("🚀 Starting efficient YOUR model...")
        
        # Start model loading
        import threading
        model_thread = threading.Thread(target=load_your_lora_model)
        model_thread.daemon = True
        model_thread.start()
        
        # Start bot
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("📱 Bot active - model loading in background...")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
