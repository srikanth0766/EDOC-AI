"""
Optimization analyzer combining heuristics and LLM suggestions.
Provides code quality and performance improvement recommendations.
"""

import ast
from typing import List, Dict
from llm_providers.base import LLMProvider


class OptimizationAnalyzer:
    """
    Analyzes code for optimization opportunities.
    Uses both rule-based heuristics and LLM-based suggestions.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize optimization analyzer.
        
        Args:
            llm_provider: LLM provider instance for deep analysis
        """
        self.llm = llm_provider
    
    def suggest(self, code: str) -> List[Dict]:
        """
        Generate optimization suggestions for code.
        
        Args:
            code: Python source code to analyze
            
        Returns:
            List of optimization suggestions, each as a dict
        """
        suggestions = []
        
        # Step 1: Run fast heuristic checks
        heuristic_suggestions = self._heuristic_checks(code)
        suggestions.extend(heuristic_suggestions)
        
        # Step 2: Get LLM-based suggestions (if available)
        if self.llm.is_available():
            try:
                llm_suggestions = self.llm.suggest_optimizations(code)
                suggestions.extend(llm_suggestions)
            except Exception as e:
                print(f"LLM optimization error: {e}")
        
        # Remove duplicates and limit results
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            key = (s.get('line', 0), s.get('suggestion', ''))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        return unique_suggestions[:10]  # Limit to top 10
    
    def _heuristic_checks(self, code: str) -> List[Dict]:
        """
        Run fast rule-based heuristic checks.
        
        Args:
            code: Python source code
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        try:
            tree = ast.parse(code)
            
            # Check for range(len()) pattern
            suggestions.extend(self._check_range_len(tree, code))
            
            # Check for list comprehension opportunities
            suggestions.extend(self._check_list_comprehension(tree, code))
            
            # Check for nested loops (complexity warning)
            suggestions.extend(self._check_nested_loops(tree, code))
            
            # Check for membership testing in lists
            suggestions.extend(self._check_membership_testing(tree, code))
        
        except SyntaxError:
            # If code has syntax errors, skip heuristic checks
            pass
        
        return suggestions
    
    def _check_range_len(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for range(len(x)) pattern that should use enumerate."""
        suggestions = []
        lines = code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if iter is range(len(...))
                if isinstance(node.iter, ast.Call):
                    if (isinstance(node.iter.func, ast.Name) and 
                        node.iter.func.id == 'range' and
                        len(node.iter.args) == 1):
                        
                        arg = node.iter.args[0]
                        if isinstance(arg, ast.Call):
                            if (isinstance(arg.func, ast.Name) and 
                                arg.func.id == 'len'):
                                
                                suggestions.append({
                                    "type": "readability",
                                    "line": node.lineno,
                                    "suggestion": "Use enumerate() instead of range(len())",
                                    "impact": "More Pythonic and readable",
                                    "example": "for i, item in enumerate(items):"
                                })
        
        return suggestions
    
    def _check_list_comprehension(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for loops that could be list comprehensions."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Simple heuristic: if loop body is just append, suggest comprehension
                if (len(node.body) == 1 and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Call)):
                    
                    call = node.body[0].value
                    if (isinstance(call.func, ast.Attribute) and
                        call.func.attr == 'append'):
                        
                        suggestions.append({
                            "type": "readability",
                            "line": node.lineno,
                            "suggestion": "Consider using list comprehension",
                            "impact": "More concise and Pythonic",
                            "example": "result = [item for item in items]"
                        })
        
        return suggestions
    
    def _check_nested_loops(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for nested loops (potential O(n²) complexity)."""
        suggestions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if body contains another for loop
                for child in ast.walk(node):
                    if child != node and isinstance(child, ast.For):
                        suggestions.append({
                            "type": "performance",
                            "line": node.lineno,
                            "suggestion": "Nested loops detected - consider optimizing",
                            "impact": "May have O(n²) time complexity",
                            "example": "Consider using sets, dicts, or different algorithm"
                        })
                        break  # Only report once per outer loop
        
        return suggestions
    
    def _check_membership_testing(self, tree: ast.AST, code: str) -> List[Dict]:
        """Check for 'in' operator used with lists (should use sets)."""
        suggestions = []
        
        # This is a simplified check - would need more context for real analysis
        # For MVP, we'll let the LLM handle this more intelligently
        
        return suggestions
