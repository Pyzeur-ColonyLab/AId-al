#!/usr/bin/env python3
"""Load YOUR LoRA fine-tuned model properly"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import login

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
tokenizer = None

def load_your_lora_model():
    global model, tokenizer
    try:
        # Login to HuggingFace
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            login(token=hf_token)
        
        logger.info("🎯 Loading YOUR LoRA fine-tuned model...")
        
        # Step 1: Load base Mistral model
        base_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        logger.info(f"📥 Loading base model: {base_model_name}")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        
        # Step 2: Load tokenizer
        logger.info("📝 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Step 3: Apply YOUR LoRA adapters
        lora_model_name = "Pyzeur/Code-du-Travail-mistral-finetune"
        logger.info(f"🔧 Applying YOUR LoRA adapters: {lora_model_name}")
        
        model = PeftModel.from_pretrained(
            base_model,
            lora_model_name,
            token=hf_token
        )
        
        logger.info("✅ YOUR LoRA fine-tuned model loaded successfully!")
        logger.info("🏛️ Your Code du Travail expertise is now active!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load YOUR LoRA model: {e}")
        raise

def generate_legal_response(user_question):
    """Generate response using YOUR fine-tuned model"""
    try:
        # Use your specialized prompt format
        prompt = f"<s>[INST] {user_question} [/INST]"
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt")
        
        # Generate using YOUR fine-tuned model
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean response
        if prompt in response:
            response = response.replace(prompt, "").strip()
        
        return response or "Je ne peux pas répondre à cette question."
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        return "Désolé, une erreur s'est produite."

async def start_command(update, context):
    await update.message.reply_text(
        "🤖 **Assistant Juridique Personnel**\n\n"
        "⚖️ **Modèle Fine-tuné sur le Code du Travail**\n"
        "🎯 **VOTRE modèle spécialisé**: Code-du-Travail-mistral-finetune\n"
        "🧠 **Base**: Mistral 7B + LoRA Adapters\n\n"
        "💼 **Expertise spécialisée en:**\n"
        "• Droit du travail français\n"
        "• Code du Travail\n"
        "• Jurisprudence sociale\n"
        "• Procédures légales\n\n"
        "❓ **Posez vos questions juridiques!**\n"
        "🎯 *Réponses de VOTRE modèle entraîné*"
    )

async def info_command(update, context):
    info_text = """
🤖 **Votre Modèle IA Personnalisé**
- **Modèle**: Code-du-Travail-mistral-finetune
- **Type**: LoRA Fine-tuning
- **Base**: Mistral 7B Instruct v0.3
- **Spécialisation**: Code du Travail FR
- **Statut**: ✅ VOTRE modèle actif
- **Entraînement**: Personnalisé
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 Question pour VOTRE modèle: {user_message}")
        
        # Show typing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate using YOUR model
        response = generate_legal_response(user_message)
        
        logger.info(f"🤖 Réponse de VOTRE modèle: {response[:100]}...")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        await update.message.reply_text("⚠️ Erreur avec votre modèle. Veuillez réessayer.")

def main():
    try:
        logger.info("🚀 Initializing YOUR fine-tuned legal AI...")
        
        # Load YOUR model
        load_your_lora_model()
        
        # Create bot
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("✅ YOUR specialized legal AI is ready!")
        logger.info("📱 YOUR custom model service active...")
        
        # Run bot
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start YOUR model: {e}")
        logger.info("🔄 Container staying alive for debugging...")
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
