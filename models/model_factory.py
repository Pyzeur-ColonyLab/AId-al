from typing import Dict, Type
from .base_model import BaseModel
from config.settings import settings

# Import your model implementations here
# from .transformer_model import TransformerModel
# from .custom_model import CustomModel

class ModelFactory:
    """Factory class for creating model instances"""
    
    _models: Dict[str, Type[BaseModel]] = {
        # Register your models here
        # "transformer": TransformerModel,
        # "custom": CustomModel,
    }
    
    @classmethod
    def create_model(cls, model_name: str = None) -> BaseModel:
        """Create a model instance based on the model name"""
        model_name = model_name or settings.MODEL_NAME
        
        if model_name not in cls._models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_class = cls._models[model_name]
        return model_class()
    
    @classmethod
    def register_model(cls, name: str, model_class: Type[BaseModel]):
        """Register a new model type"""
        cls._models[name] = model_class
    
    @classmethod
    def list_models(cls) -> list:
        """List all available models"""
        return list(cls._models.keys())