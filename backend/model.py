"""
Model wrapper for CodeBERT-based error detection.
Uses a pretrained CodeBERT model for code embeddings and a simple classifier.
"""

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from typing import Tuple


class ErrorDetectionModel:
    """Wrapper class for error detection using CodeBERT."""
    
    # Error type mapping
    ERROR_TYPES = ["IndexError", "RuntimeError", "ImportError", "Unknown"]
    
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        """
        Initialize the error detection model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        print(f"Loading model: {model_name}...")
        
        # Load tokenizer and pretrained model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.encoder = AutoModel.from_pretrained(model_name)
        
        # Set to evaluation mode
        self.encoder.eval()
        
        # Simple classifier: embedding_dim -> num_classes
        # CodeBERT base has 768-dimensional embeddings
        embedding_dim = self.encoder.config.hidden_size
        num_classes = len(self.ERROR_TYPES)
        
        # For MVP: randomly initialized classifier
        self.classifier = nn.Linear(embedding_dim, num_classes)
        self.classifier.eval()
        
        print("Model loaded successfully!")
    
    def predict(self, code: str) -> Tuple[str, float]:
        """
        Predict the error type for given Python code.
        
        Args:
            code: Python source code as string
            
        Returns:
            Tuple of (error_type, confidence)
        """
        # Tokenize the code
        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True
        )
        
        # Get embeddings from CodeBERT
        with torch.no_grad():
            outputs = self.encoder(**inputs)
            # Use [CLS] token embedding (first token)
            embedding = outputs.last_hidden_state[:, 0, :]
            
            # Pass through classifier
            logits = self.classifier(embedding)
            
            # Get probabilities
            probs = torch.softmax(logits, dim=-1)
            
            # Get prediction
            predicted_idx = torch.argmax(probs, dim=-1).item()
            confidence = probs[0, predicted_idx].item()
            
            error_type = self.ERROR_TYPES[predicted_idx]
            
        return error_type, confidence
