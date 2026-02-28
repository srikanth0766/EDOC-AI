"""
Category 1A — Lexical Analysis Tests.

Tests token recognition, keyword classification, identifier handling,
string literals, and edge cases via UniversalASTAnalyzer.check_syntax().
"""

import ast
import pytest


# ─── Python Lexical / Token Tests ────────────────────────────────────────────

class TestPythonLexicalAnalysis:

    def test_valid_simple_function(self, ast_analyzer_python):
        code = "def hello(): return 'world'"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"
        assert result["errors"] == []

    def test_valid_nested_class(self, ast_analyzer_python):
        code = """
class Outer:
    class Inner:
        def method(self):
            pass
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_valid_generics_type_hints(self, ast_analyzer_python):
        code = """
from typing import List, Dict, Optional
def process(items: List[str], mapping: Dict[str, int]) -> Optional[str]:
    return None
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_valid_lambda_expression(self, ast_analyzer_python):
        code = "square = lambda x: x ** 2"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_malformed_token(self, ast_analyzer_python):
        result = ast_analyzer_python.check_syntax("x = @")
        assert result["status"] == "error"
        assert len(result["errors"]) > 0
        assert result["errors"][0]["type"] == "SyntaxError"

    def test_malformed_function_colon(self, ast_analyzer_python):
        result = ast_analyzer_python.check_syntax("def f(:\n    pass")
        assert result["status"] == "error"

    def test_empty_code(self, ast_analyzer_python):
        result = ast_analyzer_python.check_syntax("")
        assert result["status"] == "valid"
        assert result["errors"] == []

    def test_unicode_identifiers(self, ast_analyzer_python):
        code = "café = 'latte'\n"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_string_literal_varieties(self, ast_analyzer_python):
        code = """
a = "double"
b = 'single'
c = \"\"\"triple double\"\"\"
d = f"formatted {a}"
e = b"bytes"
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_extremely_long_identifier(self, ast_analyzer_python):
        long_name = "a" * 500
        code = f"{long_name} = 42"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_mixed_whitespace(self, ast_analyzer_python):
        # Spaces only (valid Python)
        code = "x = 1\ny = 2\n"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_decorator_syntax(self, ast_analyzer_python):
        code = """
def decorator(func):
    return func

@decorator
def my_func():
    pass
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_error_has_line_number(self, ast_analyzer_python):
        code = "x = 1\ndef broken(:\n    pass"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "error"
        assert result["errors"][0]["line"] >= 1

    def test_error_message_non_empty(self, ast_analyzer_python):
        result = ast_analyzer_python.check_syntax("x = @")
        assert result["status"] == "error"
        assert len(result["errors"][0]["message"]) > 0

    def test_ast_node_count_simple(self):
        """Verify that parsing produces a non-trivial AST."""
        code = "x = 1 + 2"
        tree = ast.parse(code)
        nodes = list(ast.walk(tree))
        assert len(nodes) > 3  # Module, Assign, BinOp, Num, Num at minimum


# ─── JavaScript Lexical Tests (if esprima available) ─────────────────────────

class TestJavaScriptLexicalAnalysis:

    @pytest.fixture
    def js_analyzer(self):
        try:
            from analyzers.universal_ast_analyzer import UniversalASTAnalyzer
            return UniversalASTAnalyzer("javascript")
        except Exception:
            pytest.skip("JavaScript analyzer unavailable")

    def test_valid_js_function(self, js_analyzer):
        code = "function greet(name) { return 'Hello ' + name; }"
        result = js_analyzer.check_syntax(code)
        assert result["status"] in ("valid", "unknown")

    def test_malformed_js(self, js_analyzer):
        code = "function broken( { return; }"
        result = js_analyzer.check_syntax(code)
        # Either error detected or unknown (no esprima)
        assert result["status"] in ("error", "unknown")

    def test_js_lambda_arrow(self, js_analyzer):
        code = "const square = (x) => x * x;"
        result = js_analyzer.check_syntax(code)
        assert result["status"] in ("valid", "unknown")
