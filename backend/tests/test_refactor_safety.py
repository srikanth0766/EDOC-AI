"""
Category 5 — Refactoring Agent Safety Tests.

Tests RefactorAgent for:
  - Syntax preservation (output always valid Python)
  - Rollback on bad LLM output
  - Idempotency
  - No-LLM graceful degradation
  - All 6 smell types handled without crash
"""

import ast
import pytest
from unittest.mock import MagicMock, patch


ALL_SMELLS = [
    "long_method",
    "god_class",
    "feature_envy",
    "large_parameter_list",
    "deep_nesting",
    "high_complexity",
]


class TestRefactorSafety:

    # ── No-LLM Degradation ────────────────────────────────────────────────────

    def test_no_llm_returns_failure_gracefully(self, refactor_agent_no_llm, long_method_code):
        result = refactor_agent_no_llm.refactor(long_method_code, "long_method")
        assert result["success"] is False
        assert result["refactored_code"] == long_method_code
        assert "notes" in result and len(result["notes"]) > 0

    def test_no_llm_all_smells_no_crash(self, refactor_agent_no_llm, clean_code):
        for smell in ALL_SMELLS:
            result = refactor_agent_no_llm.refactor(clean_code, smell)
            assert isinstance(result, dict)
            assert "success" in result
            assert "refactored_code" in result

    def test_no_llm_original_code_preserved(self, refactor_agent_no_llm, long_method_code):
        result = refactor_agent_no_llm.refactor(long_method_code, "long_method")
        assert result["original_code"] == long_method_code
        assert result["refactored_code"] == long_method_code

    def test_no_llm_has_strategy_field(self, refactor_agent_no_llm, clean_code):
        result = refactor_agent_no_llm.refactor(clean_code, "long_method")
        assert "strategy" in result and len(result["strategy"]) > 0

    # ── Syntax Preservation (Mock LLM) ────────────────────────────────────────

    def test_syntax_preserved_on_good_llm_output(self, long_method_code):
        """Mock LLM that returns valid Python → refactored_code must be valid."""
        good_output = """```python
def part1(x):
    total = 0
    for i in range(1, 17):
        total += x * i
    return total

def part2(x):
    total = 0
    for i in range(17, 33):
        total += x * i
    return total
```"""
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = good_output
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        # Whether success or not, refactored_code must parse
        assert agent._is_valid_python(result["refactored_code"])

    def test_rollback_on_invalid_llm_output(self, long_method_code):
        """Mock LLM that returns broken Python → rollback to original."""
        bad_output = "def BROKEN SYNTAX HERE(:\n    @@INVALID@@"
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = bad_output
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        assert result["success"] is False
        assert result["refactored_code"] == long_method_code
        assert "rolled back" in result["notes"].lower() or "failed" in result["notes"].lower()

    def test_rollback_keeps_original_parseable(self, long_method_code):
        """After rollback, original code must still be valid Python."""
        bad_output = "not valid python at all : @@@"
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = bad_output
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        try:
            ast.parse(result["refactored_code"])
        except SyntaxError:
            pytest.fail("Rolled-back code is not valid Python!")

    # ── Idempotency ───────────────────────────────────────────────────────────

    def test_idempotency_no_llm(self, refactor_agent_no_llm, clean_code):
        """Calling refactor twice on clean code must produce same result."""
        result1 = refactor_agent_no_llm.refactor(clean_code, "long_method")
        result2 = refactor_agent_no_llm.refactor(clean_code, "long_method")
        assert result1["refactored_code"] == result2["refactored_code"]

    def test_idempotency_mock_llm(self, long_method_code):
        """Deterministic LLM mock → two refactor calls produce same output."""
        fixed_output = """```python
def extracted():
    return 42
```"""
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = fixed_output
        agent._llm = mock_llm

        r1 = agent.refactor(long_method_code, "long_method")
        r2 = agent.refactor(long_method_code, "long_method")
        assert r1["refactored_code"] == r2["refactored_code"]

    # ── Code Extraction Logic ─────────────────────────────────────────────────

    def test_extract_code_python_fence(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        raw = "Some text\n```python\ndef f(): return 1\n```\nEnd"
        extracted = agent._extract_code(raw)
        assert "def f(): return 1" in extracted

    def test_extract_code_generic_fence(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        raw = "```\ndef g(): pass\n```"
        extracted = agent._extract_code(raw)
        assert "def g(): pass" in extracted

    def test_extract_code_fallback_plain(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        raw = "def plain(): pass"
        extracted = agent._extract_code(raw)
        assert extracted == "def plain(): pass"

    # ── Python Validation ─────────────────────────────────────────────────────

    def test_is_valid_python_true(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        assert agent._is_valid_python("def f(): return 1") is True

    def test_is_valid_python_false(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        assert agent._is_valid_python("def BROKEN(: @@") is False

    def test_is_valid_python_empty(self):
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        agent._llm = None
        assert agent._is_valid_python("") is False

    # ── LLM Error Handling ────────────────────────────────────────────────────

    def test_llm_exception_triggers_graceful_failure(self, long_method_code):
        """If LLM.generate() raises an exception, agent must not crash."""
        from refactor_agent.refactor_agent import RefactorAgent
        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = RuntimeError("LLM timeout")
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        assert result["success"] is False
        assert result["refactored_code"] == long_method_code
        assert "error" in result["notes"].lower()
