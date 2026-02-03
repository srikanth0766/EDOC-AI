"""
Abstract base class for LLM providers.
Defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def analyze_logic(self, code: str) -> List[str]:
        """
        Analyze code for logical errors and edge cases.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of logical concerns/warnings as strings
        """
        pass
    
    @abstractmethod
    def suggest_optimizations(self, code: str) -> List[Dict]:
        """
        Suggest code optimizations and improvements.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of optimization suggestions, each as a dict with:
            - type: str (e.g., "performance", "readability", "safety")
            - line: int (line number, 0 if general)
            - suggestion: str (description of improvement)
            - impact: str (expected impact)
            - example: str (optional code example)
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available and configured.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
