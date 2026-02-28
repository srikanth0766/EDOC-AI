"""
Category 1B — Syntax Analysis Tests.

Tests parser correctness for deeply nested structures, complex constructs,
error recovery, and meaningful error messages.
"""

import ast
import pytest


class TestPythonSyntaxAnalysis:

    def test_deeply_nested_conditionals(self, ast_analyzer_python):
        """10-level nested if statements should parse correctly."""
        indent = "    "
        code = ""
        for level in range(10):
            code += (indent * level) + f"if True:\n"
        code += (indent * 10) + "pass\n"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_10_level_nested_loops(self, ast_analyzer_python):
        """10-level nested for loops — extreme nesting edge case."""
        indent = "    "
        code = ""
        for level in range(10):
            code += (indent * level) + f"for i{level} in range(2):\n"
        code += (indent * 10) + "pass\n"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_abstract_class_pattern(self, ast_analyzer_python):
        code = """
from abc import ABC, abstractmethod

class AbstractBase(ABC):
    @abstractmethod
    def do_work(self) -> None:
        pass

class ConcreteImpl(AbstractBase):
    def do_work(self) -> None:
        print("working")
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_annotations_and_decorators(self, ast_analyzer_python):
        code = """
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def annotated_func(x: int, y: str = "default") -> bool:
    return bool(x)
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_try_except_finally(self, ast_analyzer_python):
        code = """
try:
    result = 1 / 0
except ZeroDivisionError as e:
    result = 0
except (ValueError, TypeError):
    result = -1
else:
    print("success")
finally:
    print("done")
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_enum_pattern(self, ast_analyzer_python):
        code = """
from enum import Enum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_broken_syntax_file_returns_error(self, ast_analyzer_python):
        code = """
class Broken
    def __init__(self):
        pass
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_error_line_number_accurate(self, ast_analyzer_python):
        """Error should point to the actual broken line."""
        code = "x = 1\ny = 2\nz = @\n"
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "error"
        # Line 3 has the error
        assert result["errors"][0]["line"] == 3

    def test_error_message_is_meaningful(self, ast_analyzer_python):
        result = ast_analyzer_python.check_syntax("def f(:\n    pass")
        assert result["status"] == "error"
        msg = result["errors"][0]["message"]
        assert isinstance(msg, str) and len(msg) > 0

    def test_walrus_operator(self, ast_analyzer_python):
        code = """
data = [1, 2, 3, 4, 5]
if (n := len(data)) > 3:
    print(n)
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_comprehensions(self, ast_analyzer_python):
        code = """
squares = [x**2 for x in range(10) if x % 2 == 0]
pairs = {k: v for k, v in zip('abc', [1, 2, 3])}
unique = {x for x in [1, 1, 2, 2]}
gen = (x * 2 for x in range(5))
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_multiline_string(self, ast_analyzer_python):
        code = '''
text = """
Line 1
Line 2
Line 3
"""
'''
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"

    def test_parse_tree_depth_consistent(self):
        """Verify nested AST depth grows with nesting level."""
        def get_max_depth(tree, depth=0):
            return max(
                (get_max_depth(child, depth + 1) for child in ast.iter_child_nodes(tree)),
                default=depth
            )

        simple = ast.parse("x = 1")
        nested = ast.parse("if True:\n    if True:\n        x = 1")
        assert get_max_depth(nested) > get_max_depth(simple)

    def test_async_function(self, ast_analyzer_python):
        code = """
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)
    return url
"""
        result = ast_analyzer_python.check_syntax(code)
        assert result["status"] == "valid"
