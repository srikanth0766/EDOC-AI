"""
Unit tests for Control Flow Analyzer.
Tests detection of infinite loops, unreachable code, and loop variable issues.
"""

import pytest
from analyzers.control_flow_analyzer import ControlFlowAnalyzer


def test_infinite_while_true_without_break():
    """Test detection of infinite while True loop without break"""
    code = """
while True:
    print("infinite")
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert result.has_issues
    assert len(result.issues) == 1
    assert result.issues[0].type == 'infinite_loop'
    assert 'while True without break' in result.issues[0].description
    assert result.mermaid_code != ""
    assert 'flowchart TD' in result.mermaid_code


def test_while_true_with_break_is_valid():
    """Test that while True with break is not flagged"""
    code = """
while True:
    x = input()
    if x == 'quit':
        break
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert not result.has_issues


def test_while_loop_variable_not_updated():
    """Test detection of loop variable never being modified"""
    code = """
i = 0
while i < 10:
    print(i)
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert result.has_issues
    assert result.issues[0].type == 'variable_not_updated'
    assert 'i' in result.issues[0].description


def test_while_loop_variable_updated_is_valid():
    """Test that properly updated loop variable is not flagged"""
    code = """
i = 0
while i < 10:
    print(i)
    i += 1
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert not result.has_issues


def test_unreachable_code_after_return():
    """Test detection of unreachable code after return statement"""
    code = """
def foo():
    return 5
    print("unreachable")
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert result.has_issues
    assert result.issues[0].type == 'unreachable_code'
    assert 'return' in result.issues[0].description


def test_unreachable_code_after_break():
    """Test detection of unreachable code after break statement"""
    code = """
for i in range(10):
    break
    print("unreachable")
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert result.has_issues
    assert result.issues[0].type == 'unreachable_code'


def test_valid_code_no_issues():
    """Test that valid code returns no issues"""
    code = """
def calculate(x, y):
    result = x + y
    return result

i = 0
while i < 10:
    i += 1
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert not result.has_issues
    assert len(result.issues) == 0


def test_syntax_error_returns_empty_result():
    """Test that syntax errors return empty result gracefully"""
    code = """
def foo(
    # Missing closing parenthesis
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert not result.has_issues
    assert len(result.issues) == 0
    assert result.mermaid_code == ""


def test_mermaid_graph_structure():
    """Test that generated Mermaid graph has correct structure"""
    code = """
while True:
    print("test")
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    assert 'flowchart TD' in result.mermaid_code
    assert 'start' in result.mermaid_code
    assert 'condition' in result.mermaid_code
    assert 'classDef problem' in result.mermaid_code


def test_to_dict_serialization():
    """Test that result can be serialized to dictionary"""
    code = """
while True:
    pass
"""
    analyzer = ControlFlowAnalyzer()
    result = analyzer.analyze(code)
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert 'has_issues' in result_dict
    assert 'issues' in result_dict
    assert 'mermaid_code' in result_dict
    assert isinstance(result_dict['issues'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
