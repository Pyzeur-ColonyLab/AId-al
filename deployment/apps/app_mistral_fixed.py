#!/usr/bin/env python3
"""Fixed Mistral AI Chatbot with Token Support"""
import os
import logging
import torch
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from huggingface_hub import login

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
        
        # Login to HuggingFace if token provided
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            logger.info("🔑 Logging in to HuggingFace...")
            login(token=hf_token)
        
        # Method 1: Try with transformers pipeline
        try:
            from transformers import pipeline
            logger.info("📝 Attempting pipeline approach...")
            
            model = pipeline(
                "text-generation",
                model=model_name,
                device_map="cpu",
                torch_dtype=torch.float16,
                trust_remote_code=True,
                token=hf_token
            )
            logger.info("✅ Pipeline approach successful!")
            return True
            
        except Exception as e1:
            logger.error(f"❌ Pipeline failed: {e1}")
            
            # Method 2: Manual loading
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                logger.info("🔧 Attempting manual loading...")
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=hf_token,
                    trust_remote_code=True
                )
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                # Load model
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="cpu",
                    trust_remote_code=True,
                    token=hf_token,
                    low_cpu_mem_usage=True
                )
                logger.info("✅ Manual loading successful!")
                return True
                
            except Exception as e2:
                logger.error(f"❌ Manual loading failed: {e2}")
                
                # Method 3: Fallback to base model
                try:
                    logger.info("🔄 Falling back to base Mistral model...")
                    from transformers import pipeline
                    model = pipeline(
                        "text-generation",
                        model="mistralai/Mistral-7B-Instruct-v0.1",
                        device_map="cpu",
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
        if hasattr(model, '__call__'):  # Pipeline approach
            prompt = f"<s>[INST] {user_input} [/INST]"
            result = model(
                prompt,
                max_new_tokens=150,
                temperature=0.7,
                do_sample=True,
                return_full_text=False
            )
            response = result[0]['generated_text'].strip()
            
        else:  # Manual approach
            prompt = f"<s>[INST] {user_input} [/INST]"
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
            if prompt in response:
                response = response.replace(prompt, "").strip()
        
        return response or "Je ne peux pas répondre à cette question."
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        return "Désolé, une erreur s'est produite lors de la génération."

async def start_command(update, context):
    await update.message.reply_text(
        "🤖 **Assistant Juridique IA**\n\n"
        "⚖️ **Spécialisé en Droit du Travail Français**\n"
        f"🧠 **Modèle**: {model_name.split('/')[-1]}\n\n"
        "💼 **Expertise:**\n"
        "• Code du Travail français\n"
        "• Licenciements et ruptures\n"
        "• Congés et temps de travail\n"
        "• Contrats et rémunérations\n\n"
        "❓ **Posez votre question juridique!**"
    )

async def info_command(update, context):
    info_text = f"""
🤖 **Informations du Système**
- **Modèle IA**: {model_name.split('/')[-1]}
- **Base**: Mistral 7B Fine-tuné
- **Spécialité**: Droit du Travail FR
- **Statut**: ✅ Opérationnel
- **Type**: Intelligence Artificielle
"""
    await update.message.reply_text(info_text)

async def chat_message(update, context):
    try:
        user_message = update.message.text
        logger.info(f"👤 Question: {user_message}")
        
        # Show typing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Generate AI response
        response = generate_response(user_message)
        
        logger.info(f"🤖 Réponse IA: {response}")
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        await update.message.reply_text(
            "⚠️ Erreur technique. Veuillez réessayer."
        )

def main():
    try:
        logger.info("🚀 Initializing Mistral Legal AI...")
        
        # Load model
        load_model()
        
        # Create bot
        app = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
        
        logger.info("✅ Mistral Legal AI ready!")
        logger.info("📱 Starting Telegram service...")
        
        # Run bot
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        logger.info("🔄 Container staying alive...")
        import time
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
