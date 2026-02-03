"""
Logic analyzer using LLM for detecting logical errors.
Focuses on edge cases, incorrect assumptions, and subtle bugs.
"""

from typing import List
from llm_providers.base import LLMProvider


class LogicAnalyzer:
    """
    Analyzes code for logical errors using LLM reasoning.
    These are probabilistic warnings, not guaranteed bugs.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize logic analyzer.
        
        Args:
            llm_provider: LLM provider instance for analysis
        """
        self.llm = llm_provider
    
    def analyze(self, code: str) -> List[str]:
        """
        Analyze code for logical errors and edge cases.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of logical concerns as human-readable strings
        """
        if not self.llm.is_available():
            return ["⚠️ LLM not available - logical analysis skipped"]
        
        try:
            concerns = self.llm.analyze_logic(code)
            return concerns if concerns else []
        
        except Exception as e:
            print(f"Logic analysis error: {e}")
            return [f"⚠️ Logic analysis failed: {str(e)}"]
