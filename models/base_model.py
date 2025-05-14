from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseModel(ABC):
    """Base class for all models"""
    
    @abstractmethod
    def load_model(self, model_path: str):
        """Load the model from disk"""
        pass
    
    @abstractmethod
    def predict(self, input_text: str) -> Dict[str, Any]:
        """Make a prediction"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass