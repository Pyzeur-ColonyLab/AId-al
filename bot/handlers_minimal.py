from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.model_factory import ModelFactory
from config.settings import settings
import logging
import time

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        # Skip database initialization if not available
        self.db_manager = None
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the AI model based on settings"""
        try:
            logger.info(f"Loading model: {settings.MODEL_NAME}")
            
            # Create model from settings
            self.model = ModelFactory.create_model(
                model_type=settings.MODEL_TYPE,
                model_name=settings.MODEL_NAME
            )
            
            # Load the model
            self.model.load_model()
            
            logger.info(f"✅ Model loaded successfully: {settings.MODEL_NAME}")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {e}")
            self.model = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with model info"""
        user_id = update.effective_user.id
        
        # Check if user is allowed (skip if no database)
        if hasattr(settings, 'is_user_allowed') and not settings.is_user_allowed(user_id):
            await update.message.reply_text("❌ You are not authorized to use this bot.")
            return
        
        model_info = self.model.get_model_info() if self.model else {"model_name": "Not loaded"}
        
        welcome_text = f"""
🤖 **Universal AI Assistant Bot**

Hello! I'm powered by **{model_info['model_name']}** and ready to help!

**Available Commands:**
• `/chat <message>` - Chat with the AI model
• `/ask <question>` - Ask a specific question
• `/info` - Get model information

**Examples:**
• `/chat Hello, how are you?`
• `/ask What is artificial intelligence?`
• `/info` - See current model details

Just send me a message and I'll respond using the loaded AI model! 🚀
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🤖 Model Info", callback_data="model_info"),
                InlineKeyboardButton("📚 Help", callback_data="help")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle chat command"""
        if not context.args:
            await update.message.reply_text("💬 Please provide a message to chat!\n\nExample: `/chat How are you today?`", parse_mode='Markdown')
            return
        
        message = ' '.join(context.args)
        await self._process_ai_request(update, message, request_type="chat")
    
    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ask command for questions"""
        if not context.args:
            await update.message.reply_text("❓ Please ask a question!\n\nExample: `/ask What is machine learning?`", parse_mode='Markdown')
            return
        
        question = ' '.join(context.args)
        await self._process_ai_request(update, question, request_type="question")
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current model information"""
        if not self.model:
            await update.message.reply_text("❌ No model is currently loaded.")
            return
        
        model_info = self.model.get_model_info()
        
        info_text = f"""
🤖 **Current Model Information**

**Model:** `{model_info['model_name']}`
**Type:** {model_info.get('task_type', 'Unknown')}
**Device:** {model_info.get('device', 'Unknown')}
**Max Length:** {model_info.get('max_length', 'Unknown')} tokens
**PEFT Model:** {'Yes' if model_info.get('is_peft_model', False) else 'No'}
**Status:** {'✅ Ready' if model_info.get('model_loaded', False) else '❌ Not loaded'}

**Settings:**
• Temperature: {settings.TEMPERATURE}
• Top-p: {settings.TOP_P}
• Repetition Penalty: {settings.REPETITION_PENALTY}
"""
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
    
    async def _process_ai_request(self, update: Update, text: str, request_type: str = "chat"):
        """Process AI request with universal model"""
        if not self.model:
            await update.message.reply_text("❌ Model not available. Please try again later.")
            return
        
        # Show typing indicator
        await update.message.reply_chat_action("typing")
        
        try:
            # Add processing indicator
            processing_msg = await update.message.reply_text(f"🤖 Processing your {request_type}...")
            
            start_time = time.time()
            result = self.model.predict(text)
            processing_time = time.time() - start_time
            
            # Delete processing message
            await processing_msg.delete()
            
            if result.get('error'):
                await update.message.reply_text(f"❌ Error: {result['error']}")
                return
            
            response = result.get('response', 'No response generated')
            confidence = result.get('confidence', 0.0)
            
            # Format response
            if len(response) > settings.MAX_RESPONSE_LENGTH:
                response = response[:settings.MAX_RESPONSE_LENGTH] + "..."
            
            formatted_response = f"""
🤖 **AI Response**

{response}

---
🎯 Confidence: {confidence:.1%} | ⏱️ {processing_time:.1f}s
🔧 Model: {result.get('model_name', 'Unknown')}
{'🔗 PEFT Model' if result.get('is_peft', False) else ''}
"""
            
            await update.message.reply_text(formatted_response, parse_mode='Markdown')
            
            # Add quick action buttons
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Ask Another", callback_data="new_question"),
                    InlineKeyboardButton("ℹ️ Model Info", callback_data="model_info")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("What would you like to do next?", reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"AI request processing error: {e}")
            await update.message.reply_text(
                f"❌ Error processing your {request_type}. Please try again or use a simpler request."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages - treat as chat input"""
        text = update.message.text
        
        # Default: process as AI chat
        await self._process_ai_request(update, text, request_type="message")
