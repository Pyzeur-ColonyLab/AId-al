from telegram import Update
from telegram.ext import ContextTypes
from models.model_factory import ModelFactory
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the AI model"""
        try:
            self.model = ModelFactory.create_model()
            self.model.load_model(settings.MODEL_PATH)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "Welcome! I'm your AI assistant bot.\n"
            "Commands:\n"
            "/predict <text> - Get AI prediction\n"
            "/url <name> - Get URL resource\n"
            "/contract <name> - Get smart contract address\n"
            "/add_url <name> <url> - Add new URL resource\n"
            "/add_contract <name> <address> - Add new smart contract\n"
            "/help - Show this help message"
        )
    
    async def predict(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle prediction requests"""
        if not context.args:
            await update.message.reply_text("Please provide text to analyze.")
            return
        
        text = ' '.join(context.args)
        
        try:
            result = self.model.predict(text)
            response = f"Prediction: {result['predicted_class']}\nConfidence: {result['confidence']:.2%}"
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            await update.message.reply_text("Error processing your request.")
    
    async def get_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get URL resource"""
        if not context.args:
            await update.message.reply_text("Please provide a resource name.")
            return
        
        name = context.args[0]
        resource = self.db_manager.get_url_resource(name)
        
        if resource:
            response = f"**{resource.name}**\nURL: {resource.url}\n"
            if resource.description:
                response += f"Description: {resource.description}"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(f"URL resource '{name}' not found.")
    
    async def get_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get smart contract address"""
        if not context.args:
            await update.message.reply_text("Please provide a contract name.")
            return
        
        name = context.args[0]
        contract = self.db_manager.get_smart_contract(name)
        
        if contract:
            response = f"**{contract.name}**\nAddress: {contract.address}\n"
            if contract.network:
                response += f"Network: {contract.network}\n"
            if contract.description:
                response += f"Description: {contract.description}"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(f"Smart contract '{name}' not found.")
    
    async def add_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new URL resource"""
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /add_url <name> <url> [description]")
            return
        
        name = context.args[0]
        url = context.args[1]
        description = ' '.join(context.args[2:]) if len(context.args) > 2 else None
        
        if self.db_manager.add_url_resource(name, url, description):
            await update.message.reply_text(f"URL resource '{name}' added successfully.")
        else:
            await update.message.reply_text(f"Failed to add URL resource. Name might already exist.")
    
    async def add_contract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add new smart contract"""
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /add_contract <name> <address> [network] [description]")
            return
        
        name = context.args[0]
        address = context.args[1]
        network = context.args[2] if len(context.args) > 2 else None
        description = ' '.join(context.args[3:]) if len(context.args) > 3 else None
        
        if self.db_manager.add_smart_contract(name, address, network, description):
            await update.message.reply_text(f"Smart contract '{name}' added successfully.")
        else:
            await update.message.reply_text(f"Failed to add smart contract. Name might already exist.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages"""
        text = update.message.text
        
        # Check if the message is asking about URLs or contracts
        if "url" in text.lower() or "link" in text.lower():
            resources = self.db_manager.search_resources(text)
            if resources:
                response = "Found these URL resources:\n"
                for res in resources[:5]:  # Limit to 5 results
                    response += f"- {res.name}: {res.url}\n"
                await update.message.reply_text(response)
                return
        
        if "contract" in text.lower() or "address" in text.lower():
            contracts = self.db_manager.search_contracts(text)
            if contracts:
                response = "Found these smart contracts:\n"
                for cont in contracts[:5]:  # Limit to 5 results
                    response += f"- {cont.name}: {cont.address} ({cont.network})\n"
                await update.message.reply_text(response)
                return
        
        # Otherwise, use the model for prediction
        try:
            result = self.model.predict(text)
            response = f"Analysis: {result['predicted_class']}\nConfidence: {result['confidence']:.2%}"
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text("I couldn't process your message. Please try again.")