#!/usr/bin/env python3
"""Robust Mistral AI Chatbot with Advanced Error Handling"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
tokenizer = None
model_name = os.getenv('MODEL_NAME', 'Pyzeur/Code-du-Travail-mistral-finetune')

def load_model():
    global model, tokenizer
    try:
        logger.info(f"🔄 Loading Mistral model: {model_name}")
        
        # Method 1: Try with simple pipeline
        try:
            from transformers import pipeline
            logger.info("📝 Attempting pipeline approach...")
            
            model = pipeline(
                "text-generation",
                model=model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                model_kwargs={
                    "low_cpu_mem_usage": True,
                    "use_cache": True
                }
            )
            logger.info("✅ Pipeline approach successful!")
            return True
            
        except Exception as e1:
            logger.error(f"❌ Pipeline failed: {e1}")
            
            # Method 2: Try manual loading with different tokenizer
            try:
                from transformers import AutoModelForCausalLM, LlamaTokenizer
                logger.info("🔧 Attempting manual loading with LlamaTokenizer...")
                
                # Load tokenizer
                tokenizer = LlamaTokenizer.from_pretrained(
                    "huggyllama/llama-7b",  # Compatible tokenizer
                    use_fast=False
                )
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                # Load model
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="cpu",  # Force CPU for stability
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                logger.info("✅ Manual loading successful!")
                return True
                
            except Exception as e2:
                logger.error(f"❌ Manual loading failed: {e2}")
                
                # Method 3: Try with base model fallback
                try:
                    logger.info("🔄 Falling back to base Mistral model...")
                    model = pipeline(
                        "text-generation",
                        model="mistralai/Mistral-7B-Instruct-v0.1",
                        device_map="auto",
                        torch_dtype=torch.float16
                    )
                    logger.info("✅ Base model fallback successful!")
                    return True
                    
                except Exception as e3:
                    logger.error(f"❌ All methods failed: {e3}")
                    raise Exception("Could not load any model")
                    
    except Exception as e:
        logger.error(f"❌ Fatal error loading model: {e}")
        raise

def generate_response(user_input):
    global model, tokenizer
    try:
        if hasattr(model, 'tokenizer'):  # Pipeline approach
            prompt = f"<s>[INST] {user_input} [/INST]"
            result = model(
                prompt,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                return_full_text=False
            )
            response = result[0]['generated_text'].strip()
            
        else:  # Manual approach
            prompt = f"Question: {user_input}\nRéponse:"
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            if "Réponse:" in response:
                response = response.split("Réponse:")[-1].strip()
        
        return response or "Je ne peux pas répondre à cette question."
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        return "Désolé, une erreur s'est produite lors de la génération."

async def start_command(update, context):
    await update.message.reply_text(
        "🤖 **Bonjour!** Je suis votre assistant spécialisé en **droit du travail français**.\n\n"
        "💼 **Spécialités:**\n"
        "• Code du Travail\n"
        "• Licenciements\n"
        "• Congés payés\n"
        "• Contrats de travail\n"
        "• Relations sociales\n\n"
        "❓ **Posez-moi vos questions juridiques!**"
    )

async def info_command(update, context):
    info_text = f"""
🤖 **Informations du Bot:**
- **Modèle**: {model_name.split('/')[-1]}
- **Base**: Mistral 7B Instruct v0.3
- **Spécialité**: Code du Travail Français
- **Statut**: ✅ Actif
- **Type**: Fine-tuné pour le droit du travail
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 User: {user_message}")
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate response
        response = generate_response(user_message)
        
        logger.info(f"🤖 Bot: {response}")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        await update.message.reply_text(
            "⚠️ Désolé, j'ai rencontré un problème technique. "
            "Veuillez reformuler votre question."
        )

def main():
    try:
        logger.info("🚀 Initializing Mistral Legal Assistant...")
        
        # Load model
        load_model()
        
        # Create Telegram bot
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("✅ Mistral Legal Assistant ready!")
        logger.info("📱 Starting Telegram polling...")
        
        # Run bot
        app.run_polling(
            poll_interval=1.0,
            timeout=10,
            read_timeout=30,
            write_timeout=30
        )
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.info("🔄 Keeping container alive for debugging...")
        import time
        while True:
            time.sleep(60)
            logger.info("💤 Container still running...")

if __name__ == "__main__":
    main()
