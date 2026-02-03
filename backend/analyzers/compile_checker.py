"""
Compile-time error checker using Python AST and built-in compiler.
NO AI needed - uses deterministic parsing and syntax validation.
"""

import ast
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CompileError:
    """Represents a compile-time error."""
    type: str  # "SyntaxError", "ImportError", etc.
    line: int
    column: Optional[int]
    message: str
    suggestion: str


@dataclass
class CompileTimeResult:
    """Result of compile-time analysis."""
    status: str  # "ok" or "error"
    errors: List[CompileError]
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0


class CompileTimeChecker:
    """
    AST-based compile-time error detection.
    Fast, deterministic, no AI required.
    """
    
    def check(self, code: str) -> CompileTimeResult:
        """
        Check code for compile-time errors.
        
        Args:
            code: Python source code as string
            
        Returns:
            CompileTimeResult with status and any errors found
        """
        errors = []
        
        # Step 1: Try to parse with AST
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(self._handle_syntax_error(e))
            # If syntax error, can't continue with other checks
            return CompileTimeResult(status="error", errors=errors)
        except Exception as e:
            errors.append(CompileError(
                type=type(e).__name__,
                line=0,
                column=None,
                message=str(e),
                suggestion="Fix the parsing error"
            ))
            return CompileTimeResult(status="error", errors=errors)
        
        # Step 2: Try to compile (catches some additional errors)
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            # Should have been caught by AST, but just in case
            errors.append(self._handle_syntax_error(e))
        except Exception as e:
            errors.append(CompileError(
                type=type(e).__name__,
                line=0,
                column=None,
                message=str(e),
                suggestion="Fix the compilation error"
            ))
        
        # Step 3: Check for common import issues (static analysis)
        import_errors = self._check_imports(code)
        errors.extend(import_errors)
        
        if errors:
            return CompileTimeResult(status="error", errors=errors)
        else:
            return CompileTimeResult(status="ok", errors=[])
    
    def _handle_syntax_error(self, e: SyntaxError) -> CompileError:
        """Convert SyntaxError to CompileError with helpful suggestion."""
        message = e.msg
        line = e.lineno or 0
        column = e.offset
        
        # Generate helpful suggestions based on common syntax errors
        suggestion = self._get_syntax_suggestion(message, e.text)
        
        return CompileError(
            type="SyntaxError",
            line=line,
            column=column,
            message=message,
            suggestion=suggestion
        )
    
    def _get_syntax_suggestion(self, message: str, text: Optional[str]) -> str:
        """Generate helpful suggestion for syntax errors."""
        message_lower = message.lower()
        
        if "invalid syntax" in message_lower:
            if text and "if " in text and ":" not in text:
                return "Add colon ':' after if condition"
            elif text and "def " in text and ":" not in text:
                return "Add colon ':' after function definition"
            elif text and "for " in text and ":" not in text:
                return "Add colon ':' after for statement"
            elif text and "while " in text and ":" not in text:
                return "Add colon ':' after while condition"
            else:
                return "Check syntax - missing colon, parenthesis, or bracket"
        
        elif "unexpected eof" in message_lower or "expected" in message_lower:
            return "Check for unclosed parentheses, brackets, or quotes"
        
        elif "indent" in message_lower:
            return "Fix indentation - use consistent spaces or tabs"
        
        elif "unterminated string" in message_lower:
            return "Add closing quote to string"
        
        else:
            return "Review Python syntax documentation"
    
    def _check_imports(self, code: str) -> List[CompileError]:
        """
        Check for potential import issues (static analysis only).
        Does NOT actually try to import - just checks syntax.
        """
        errors = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for relative imports without package context
                if isinstance(node, ast.ImportFrom):
                    if node.level > 0:  # Relative import
                        errors.append(CompileError(
                            type="ImportWarning",
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Relative import detected: {node.module or ''}",
                            suggestion="Relative imports may fail outside package context"
                        ))
                
                # Check for import * (not an error, but worth noting)
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.names:
                        for alias in node.names:
                            if alias.name == '*':
                                errors.append(CompileError(
                                    type="ImportWarning",
                                    line=node.lineno,
                                    column=node.col_offset,
                                    message="Wildcard import detected (import *)",
                                    suggestion="Consider importing specific names for clarity"
                                ))
        
        except Exception:
            # If AST parsing fails, we already caught it in main check
            pass
        
        return errors
    
    def to_dict(self, result: CompileTimeResult) -> Dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "status": result.status,
            "errors": [
                {
                    "type": err.type,
                    "line": err.line,
                    "column": err.column,
                    "message": err.message,
                    "suggestion": err.suggestion
                }
                for err in result.errors
            ]
        }
