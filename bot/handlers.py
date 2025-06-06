from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.model_factory import ModelFactory
from database.db_manager import DatabaseManager
from config.settings import settings
import logging
import time
import json

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.db_manager = DatabaseManager()
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
        
        # Check if user is allowed
        if not settings.is_user_allowed(user_id):
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
• `/models` - List popular models
• `/switch <model_name>` - Switch to different model (admin only)

**Resource Management:**
• `/url <name>` - Get URL resource
• `/contract <name>` - Get smart contract
• `/add_url <name> <url>` - Add URL resource
• `/add_contract <name> <address>` - Add smart contract

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
            ],
            [InlineKeyboardButton("🔄 Popular Models", callback_data="popular_models")]
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
**Task Type:** {model_info['task_type']}
**Device:** {model_info['device']}
**Max Length:** {model_info['max_length']} tokens
**Quantized:** {'Yes' if model_info.get('quantized', False) else 'No'}
**Status:** {'✅ Ready' if model_info['model_loaded'] else '❌ Not loaded'}

**Settings:**
• Temperature: {settings.TEMPERATURE}
• Top-p: {settings.TOP_P}
• Repetition Penalty: {settings.REPETITION_PENALTY}
"""
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
    
    async def models(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show popular models by category"""
        popular_models = ModelFactory.get_popular_models()
        
        models_text = "🔥 **Popular Models by Category**\n\n"
        
        for category, model_list in popular_models.items():
            models_text += f"**{category.replace('_', ' ').title()}:**\n"
            for model in model_list[:3]:  # Show top 3 per category
                models_text += f"• `{model}`\n"
            models_text += "\n"
        
        models_text += "💡 Use `/switch <model_name>` to change models (admin only)"
        
        await update.message.reply_text(models_text, parse_mode='Markdown')
    
    async def switch_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Switch to a different model (admin only)"""
        user_id = update.effective_user.id
        
        if not settings.is_admin_user(user_id):
            await update.message.reply_text("❌ This command is only available to administrators.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "🔄 **Switch Model**\n\n"
                "Usage: `/switch <model_name>`\n\n"
                "Examples:\n"
                "• `/switch gpt2`\n"
                "• `/switch microsoft/DialoGPT-medium`\n"
                "• `/switch Pyzeur/Code-du-Travail-mistral-finetune`",
                parse_mode='Markdown'
            )
            return
        
        new_model_name = ' '.join(context.args)
        
        await update.message.reply_text(f"🔄 Switching to model: `{new_model_name}`\nThis may take a moment...", parse_mode='Markdown')
        
        try:
            # Create new model instance
            new_model = ModelFactory.create_model(
                model_type="universal",
                model_name=new_model_name
            )
            
            # Load the new model
            new_model.load_model()
            
            # Replace current model
            self.model = new_model
            
            await update.message.reply_text(f"✅ Successfully switched to: `{new_model_name}`", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error switching model: {e}")
            await update.message.reply_text(f"❌ Failed to switch model: {str(e)}")
    
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
    
    # Keep existing URL and contract methods
    async def get_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get URL resource"""
        if not settings.ENABLE_URL_RESOURCES:
            await update.message.reply_text("📎 URL resources are disabled.")
            return
            
        if not context.args:
            await update.message.reply_text("📎 Please specify the resource name.")
            return
        
        name = context.args[0]
        resource = self.db_manager.get_url_resource(name)
        
        if resource:
            response = f"""
📎 **URL Resource**

**Name:** {resource.name}
**URL:** {resource.url}
"""
            if resource.description:
                response += f"**Description:** {resource.description}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ URL resource '{name}' not found.")
    
    async def get_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get smart contract"""
        if not settings.ENABLE_SMART_CONTRACTS:
            await update.message.reply_text("🔗 Smart contracts are disabled.")
            return
            
        if not context.args:
            await update.message.reply_text("🔗 Please specify the contract name.")
            return
        
        name = context.args[0]
        contract = self.db_manager.get_smart_contract(name)
        
        if contract:
            response = f"""
🔗 **Smart Contract**

**Name:** {contract.name}
**Address:** `{contract.address}`
"""
            if contract.network:
                response += f"**Network:** {contract.network}\n"
            if contract.description:
                response += f"**Description:** {contract.description}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Smart contract '{name}' not found.")
    
    async def add_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new URL resource"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "📎 Usage: `/add_url <name> <url> [description]`",
                parse_mode='Markdown'
            )
            return
        
        name = context.args[0]
        url = context.args[1]
        description = ' '.join(context.args[2:]) if len(context.args) > 2 else None
        
        if self.db_manager.add_url_resource(name, url, description):
            await update.message.reply_text(f"✅ URL resource '{name}' added successfully.")
        else:
            await update.message.reply_text(f"❌ Failed to add URL resource. Name might already exist.")
    
    async def add_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new smart contract"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "🔗 Usage: `/add_contract <name> <address> [network] [description]`",
                parse_mode='Markdown'
            )
            return
        
        name = context.args[0]
        address = context.args[1]
        network = context.args[2] if len(context.args) > 2 else None
        description = ' '.join(context.args[3:]) if len(context.args) > 3 else None
        
        if self.db_manager.add_smart_contract(name, address, network, description):
            await update.message.reply_text(f"✅ Smart contract '{name}' added successfully.")
        else:
            await update.message.reply_text(f"❌ Failed to add smart contract. Name might already exist.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages - treat as chat input"""
        text = update.message.text
        
        # Check for resource searches first
        if "url" in text.lower() or "link" in text.lower():
            resources = self.db_manager.search_resources(text)
            if resources:
                response = "🔍 **Found URL resources:**\n\n"
                for res in resources[:3]:
                    response += f"• **{res.name}**: {res.url}\n"
                await update.message.reply_text(response, parse_mode='Markdown')
                return
        
        if "contract" in text.lower() or "address" in text.lower():
            contracts = self.db_manager.search_contracts(text)
            if contracts:
                response = "🔍 **Found smart contracts:**\n\n"
                for cont in contracts[:3]:
                    response += f"• **{cont.name}**: `{cont.address}` ({cont.network})\n"
                await update.message.reply_text(response, parse_mode='Markdown')
                return
        
        # Default: process as AI chat
        await self._process_ai_request(update, text, request_type="message")
