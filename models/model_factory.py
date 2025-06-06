from .transformer_model import TransformerModel
from .universal_model import UniversalModel
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ModelFactory:
    """
    Universal Factory for creating any AI model from HuggingFace
    Supports automatic model detection and configuration
    """
    
    AVAILABLE_MODELS = {
        'transformer': TransformerModel,
        'universal': UniversalModel,
        'auto': UniversalModel,  # Alias for universal
    }
    
    @classmethod
    def create_model(cls, model_type: str = None, model_name: str = None, **kwargs):
        """
        Create and return a model instance
        
        Args:
            model_type: Type of model handler ('universal', 'transformer', 'auto')
            model_name: HuggingFace model name (e.g., 'Pyzeur/Code-du-Travail-mistral-finetune')
            **kwargs: Additional configuration parameters
        
        Returns:
            Model instance ready for loading
        """
        
        # Get model type from settings or use default
        if model_type is None:
            model_type = getattr(settings, 'MODEL_TYPE', 'universal')
        
        # Get model name from settings if not provided
        if model_name is None:
            model_name = getattr(settings, 'MODEL_NAME', 'microsoft/DialoGPT-medium')
        
        model_class = cls.AVAILABLE_MODELS.get(model_type)
        
        if not model_class:
            logger.warning(f"Unknown model type: {model_type}. Using UniversalModel")
            model_class = UniversalModel
        
        logger.info(f"Creating {model_type} model with {model_name}")
        
        # Create model instance with configuration
        if model_class == UniversalModel:
            return model_class(model_name=model_name, model_config=kwargs)
        else:
            return model_class(**kwargs)
    
    @classmethod
    def create_from_config(cls, config: dict):
        """
        Create model from configuration dictionary
        
        Args:
            config: Dictionary containing model configuration
                   Example: {
                       'model_name': 'Pyzeur/Code-du-Travail-mistral-finetune',
                       'model_type': 'universal',
                       'max_length': 512,
                       'use_quantization': True
                   }
        """
        model_type = config.get('model_type', 'universal')
        model_name = config.get('model_name', 'microsoft/DialoGPT-medium')
        
        # Remove model_type and model_name from kwargs
        kwargs = {k: v for k, v in config.items() if k not in ['model_type', 'model_name']}
        
        return cls.create_model(model_type=model_type, model_name=model_name, **kwargs)
    
    @classmethod
    def list_available_models(cls):
        """List all available model types"""
        return list(cls.AVAILABLE_MODELS.keys())
    
    @classmethod
    def get_popular_models(cls):
        """Get a list of popular/recommended models by category"""
        return {
            'chat_models': [
                'microsoft/DialoGPT-medium',
                'microsoft/DialoGPT-large',
                'facebook/blenderbot-400M-distill',
                'Pyzeur/Code-du-Travail-mistral-finetune'  # Your model
            ],
            'generation_models': [
                'gpt2',
                'gpt2-medium',
                'mistralai/Mistral-7B-Instruct-v0.1',
                'microsoft/phi-2',
                'google/gemma-2b-it'
            ],
            'classification_models': [
                'cardiffnlp/twitter-roberta-base-sentiment-latest',
                'nlptown/bert-base-multilingual-uncased-sentiment',
                'distilbert-base-uncased-finetuned-sst-2-english'
            ],
            'qa_models': [
                'distilbert-base-cased-distilled-squad',
                'deepset/roberta-base-squad2',
                'google/tapas-base-finetuned-wtq'
            ],
            'multilingual_models': [
                'Helsinki-NLP/opus-mt-en-fr',
                'google/mt5-small',
                'facebook/mbart-large-50-many-to-many-mmt'
            ]
        }
    
    @classmethod
    def get_model_recommendations(cls, use_case: str = 'chat'):
        """
        Get model recommendations based on use case
        
        Args:
            use_case: 'chat', 'classification', 'qa', 'generation', 'translation'
        """
        recommendations = {
            'chat': [
                {
                    'name': 'Pyzeur/Code-du-Travail-mistral-finetune',
                    'description': 'Fine-tuned model for French legal/work code questions',
                    'best_for': 'French legal queries and Code du Travail questions'
                },
                {
                    'name': 'microsoft/DialoGPT-medium',
                    'description': 'General purpose conversational model',
                    'best_for': 'General chat and conversation'
                },
                {
                    'name': 'mistralai/Mistral-7B-Instruct-v0.1',
                    'description': 'Powerful instruction-following model',
                    'best_for': 'Complex reasoning and detailed responses'
                }
            ],
            'classification': [
                {
                    'name': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
                    'description': 'Sentiment analysis model',
                    'best_for': 'Analyzing sentiment in text'
                }
            ],
            'qa': [
                {
                    'name': 'distilbert-base-cased-distilled-squad',
                    'description': 'Question answering model',
                    'best_for': 'Extracting answers from documents'
                }
            ],
            'generation': [
                {
                    'name': 'gpt2-medium',
                    'description': 'Text generation model',
                    'best_for': 'Creative writing and text completion'
                }
            ]
        }
        
        return recommendations.get(use_case, recommendations['chat'])
