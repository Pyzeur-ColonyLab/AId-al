from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any
from .base_model import BaseModel

class TransformerModel(BaseModel):
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def load_model(self, model_path: str):
        """Load the transformer model"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
    
    def predict(self, input_text: str) -> Dict[str, Any]:
        """Make prediction using the transformer model"""
        inputs = self.tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(predictions, dim=-1).item()
            confidence = predictions[0][predicted_class].item()
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "raw_outputs": outputs.logits.cpu().numpy().tolist()
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "type": "transformer",
            "device": str(self.device),
            "loaded": self.model is not None
        }