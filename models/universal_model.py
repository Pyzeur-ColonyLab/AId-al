"""
Universal Model Handler for any HuggingFace model
Supports text generation, classification, and Q&A tasks
"""

import torch
import logging
from typing import Dict, Any, Optional, List
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    AutoModelForSequenceClassification,
    AutoModelForQuestionAnswering,
    pipeline,
    BitsAndBytesConfig
)
from .base_model import BaseModel
from config.settings import settings
import json
import re

logger = logging.getLogger(__name__)

class UniversalModel(BaseModel):
    """
    Universal model handler that can work with any HuggingFace model
    Automatically detects model type and configures appropriate pipelines
    """
    
    def __init__(self, model_name: str = None, model_config: Dict = None):
        super().__init__()
        self.model_name = model_name or getattr(settings, 'MODEL_NAME', 'microsoft/DialoGPT-medium')
        self.model_config = model_config or {}
        
        # Model components
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        # Device and optimization settings
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_quantization = getattr(settings, 'USE_QUANTIZATION', False)
        self.max_length = int(getattr(settings, 'MAX_LENGTH', 512))
        
        # Task detection
        self.task_type = None
        self.supported_tasks = [
            'text-generation', 'text2text-generation', 'question-answering',
            'text-classification', 'conversational'
        ]
        
        logger.info(f"Initializing UniversalModel with {self.model_name}")
    
    def load_model(self, model_path: str = None):
        """Load any HuggingFace model dynamically"""
        try:
            model_name = model_path or self.model_name
            logger.info(f"Loading model: {model_name}")
            
            # Load tokenizer first
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add special tokens if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Detect task type from model config
            self.task_type = self._detect_task_type(model_name)
            
            # Configure quantization if enabled
            quantization_config = None
            if self.use_quantization and torch.cuda.is_available():
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load model based on detected task
            if self.task_type in ['text-generation', 'text2text-generation', 'conversational']:
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    quantization_config=quantization_config,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
            elif self.task_type == 'text-classification':
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
            elif self.task_type == 'question-answering':
                self.model = AutoModelForQuestionAnswering.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    trust_remote_code=True
                )
            
            # Create pipeline
            self._create_pipeline()
            
            logger.info(f"✅ Model loaded successfully: {model_name} ({self.task_type})")
            
        except Exception as e:
            logger.error(f"❌ Error loading model {model_name}: {e}")
            raise
    
    def _detect_task_type(self, model_name: str) -> str:
        """Detect the task type based on model name and config"""
        model_name_lower = model_name.lower()
        
        # Check model name patterns
        if any(pattern in model_name_lower for pattern in ['gpt', 'llama', 'mistral', 'gemma', 'phi']):
            return 'text-generation'
        elif any(pattern in model_name_lower for pattern in ['t5', 'bart', 'pegasus']):
            return 'text2text-generation'
        elif any(pattern in model_name_lower for pattern in ['bert', 'roberta', 'distilbert']) and 'qa' in model_name_lower:
            return 'question-answering'
        elif any(pattern in model_name_lower for pattern in ['bert', 'roberta', 'distilbert']):
            return 'text-classification'
        elif 'dialogpt' in model_name_lower:
            return 'conversational'
        
        # Default to text generation for chat models
        return 'text-generation'
    
    def _create_pipeline(self):
        """Create appropriate pipeline based on task type"""
        try:
            pipeline_kwargs = {
                "model": self.model,
                "tokenizer": self.tokenizer,
                "device": 0 if torch.cuda.is_available() else -1,
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            }
            
            if self.task_type == 'text-generation':
                pipeline_kwargs.update({
                    "do_sample": True,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_new_tokens": self.max_length,
                    "repetition_penalty": 1.1,
                    "pad_token_id": self.tokenizer.eos_token_id,
                })
                
            self.pipeline = pipeline(self.task_type, **pipeline_kwargs)
            logger.info(f"✅ Created {self.task_type} pipeline")
            
        except Exception as e:
            logger.error(f"❌ Error creating pipeline: {e}")
            raise
    
    def predict(self, text: str, **kwargs) -> Dict[str, Any]:
        """Universal prediction method that adapts to any model type"""
        try:
            if not self.pipeline:
                raise ValueError("Model not loaded")
            
            # Route to appropriate prediction method
            if self.task_type in ['text-generation', 'conversational']:
                return self._generate_text(text, **kwargs)
            elif self.task_type == 'text2text-generation':
                return self._generate_text_to_text(text, **kwargs)
            elif self.task_type == 'question-answering':
                return self._answer_question(text, **kwargs)
            elif self.task_type == 'text-classification':
                return self._classify_text(text, **kwargs)
            else:
                return self._generate_text(text, **kwargs)  # Fallback
                
        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            return {
                'response': f"Error processing request: {str(e)}",
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _generate_text(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text for chat/completion models"""
        try:
            # Format prompt based on model type
            formatted_prompt = self._format_prompt(prompt)
            
            # Generate response
            outputs = self.pipeline(
                formatted_prompt,
                max_new_tokens=kwargs.get('max_tokens', self.max_length),
                do_sample=kwargs.get('do_sample', True),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 0.9),
                repetition_penalty=kwargs.get('repetition_penalty', 1.1),
                return_full_text=False,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
            generated_text = outputs[0]['generated_text'].strip()
            cleaned_response = self._clean_response(generated_text)
            
            return {
                'response': cleaned_response,
                'confidence': self._calculate_confidence(cleaned_response),
                'model_name': self.model_name,
                'task_type': self.task_type
            }
            
        except Exception as e:
            logger.error(f"❌ Text generation error: {e}")
            return {'response': "I couldn't generate a response.", 'confidence': 0.0, 'error': str(e)}
    
    def _generate_text_to_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text-to-text generation models (T5, BART, etc.)"""
        try:
            outputs = self.pipeline(text, max_length=self.max_length)
            response = outputs[0]['generated_text'] if outputs else "No response generated"
            
            return {
                'response': response,
                'confidence': self._calculate_confidence(response),
                'model_name': self.model_name,
                'task_type': self.task_type
            }
            
        except Exception as e:
            return {'response': "Error in text-to-text generation", 'confidence': 0.0, 'error': str(e)}
    
    def _answer_question(self, text: str, context: str = None, **kwargs) -> Dict[str, Any]:
        """Handle question-answering models"""
        try:
            if context is None:
                # If no context provided, use the text as both question and context
                context = text
                question = text
            else:
                question = text
            
            result = self.pipeline(question=question, context=context)
            
            return {
                'response': result['answer'],
                'confidence': result['score'],
                'model_name': self.model_name,
                'task_type': self.task_type
            }
            
        except Exception as e:
            return {'response': "Error in question answering", 'confidence': 0.0, 'error': str(e)}
    
    def _classify_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """Handle text classification models"""
        try:
            results = self.pipeline(text)
            
            if isinstance(results, list) and results:
                best_result = max(results, key=lambda x: x['score'])
                response = f"Classification: {best_result['label']}"
            else:
                response = f"Classification: {results['label']}"
                best_result = results
            
            return {
                'response': response,
                'confidence': best_result['score'],
                'predicted_class': best_result['label'],
                'model_name': self.model_name,
                'task_type': self.task_type
            }
            
        except Exception as e:
            return {'response': "Error in text classification", 'confidence': 0.0, 'error': str(e)}
    
    def _format_prompt(self, text: str) -> str:
        """Format prompt based on model type and training template"""
        model_name_lower = self.model_name.lower()
        
        # Check for specific model formats
        if 'mistral' in model_name_lower or 'mixtral' in model_name_lower:
            return f"<s>[INST] {text} [/INST]"
        elif 'llama' in model_name_lower and 'chat' in model_name_lower:
            return f"<s>[INST] {text} [/INST]"
        elif 'phi' in model_name_lower:
            return f"Instruct: {text}\nOutput:"
        elif 'gemma' in model_name_lower:
            return f"<start_of_turn>user\n{text}<end_of_turn>\n<start_of_turn>model\n"
        elif any(pattern in model_name_lower for pattern in ['gpt', 'dialogpt']):
            return text
        else:
            # Generic format - just return the text
            return text
    
    def _clean_response(self, response: str) -> str:
        """Clean generated response"""
        # Remove special tokens and artifacts
        response = re.sub(r'<[^>]+>', '', response)  # Remove XML-like tags
        response = re.sub(r'\[INST\]|\[/INST\]', '', response)  # Remove instruction tokens
        response = re.sub(r'<start_of_turn>|<end_of_turn>', '', response)  # Remove turn tokens
        response = re.sub(r'\s+', ' ', response)  # Normalize whitespace
        
        # Remove repetitive patterns
        lines = response.split('\n')
        unique_lines = []
        for line in lines:
            if line.strip() and line.strip() not in unique_lines:
                unique_lines.append(line.strip())
        
        return '\n'.join(unique_lines).strip()
    
    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score based on response characteristics"""
        if not response or len(response.strip()) < 3:
            return 0.0
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on response length
        word_count = len(response.split())
        if word_count < 3:
            confidence -= 0.3
        elif word_count > 10:
            confidence += 0.1
        
        # Check for completeness indicators
        if response.endswith(('.', '!', '?')):
            confidence += 0.1
        
        # Penalize very short or very long responses
        if len(response) < 10:
            confidence -= 0.2
        elif len(response) > 1000:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def chat(self, message: str, history: List[str] = None) -> str:
        """Simple chat interface"""
        result = self.predict(message)
        return result.get('response', 'I could not generate a response.')
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'task_type': self.task_type,
            'device': str(self.device),
            'max_length': self.max_length,
            'quantized': self.use_quantization,
            'model_loaded': self.model is not None,
            'pipeline_ready': self.pipeline is not None
        }
