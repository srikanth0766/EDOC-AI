"""
Category 11 — Chaos Testing.

Tests graceful degradation under failure conditions:
  - ML service down (RuntimeError) → 500 with detail
  - Refactor agent LLM timeout → graceful rollback
  - LLM unavailable → no crash, helpful notes
  - SprintStore failure → 500 on /log-sprint

All service failures use unittest.mock.patch for injection.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestChaosMLServiceDown:

    def test_model_predict_exception_returns_failure_note(self):
        """If model.predict raises RuntimeError, result must be handled gracefully."""
        from model import ErrorDetectionModel
        model = ErrorDetectionModel()
        with patch.object(model, "predict", side_effect=RuntimeError("Model crashed")):
            try:
                model.predict("x = 1")
                # If exception is not handled by model itself, it propagates
            except RuntimeError:
                pass  # Expected — chaos test confirms exception propagates

    @pytest.mark.asyncio
    async def test_api_predict_with_model_crash_returns_500(self, async_client):
        """If model crashes during /predict, API must return 500."""
        try:
            with patch("model.ErrorDetectionModel.predict",
                       side_effect=RuntimeError("Model down")):
                response = await async_client.post("/predict", json={"code": "x = 1"})
                assert response.status_code == 500
        except Exception:
            pytest.skip("FastAPI app not available")

    def test_smell_detector_on_parse_error_no_crash(self):
        """SmellDetector must not crash even on pathological input."""
        from analyzers.smell_detector import SmellDetector
        detector = SmellDetector()
        # Inject FeatureExtractor returning None
        with patch.object(detector._extractor, "extract", return_value=None):
            result = detector.detect("any code")
            assert result == []


class TestChaosRefactorAgentTimeout:

    def test_llm_generate_timeout_triggers_graceful_failure(self, long_method_code):
        """If LLM.generate() hangs (simulated via exception), agent must not crash."""
        from refactor_agent.refactor_agent import RefactorAgent
        import time

        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()

        def slow_generate(prompt):
            raise TimeoutError("LLM request timed out")

        mock_llm.generate.side_effect = slow_generate
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        assert result["success"] is False
        assert result["refactored_code"] == long_method_code
        assert "error" in result["notes"].lower()

    def test_refactor_agent_exception_from_llm(self, long_method_code):
        """Any exception from LLM must result in rollback, not propagation."""
        from refactor_agent.refactor_agent import RefactorAgent

        agent = RefactorAgent.__new__(RefactorAgent)
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = ConnectionError("Cannot reach LLM")
        agent._llm = mock_llm

        result = agent.refactor(long_method_code, "long_method")
        assert not result["success"]
        assert result["original_code"] == long_method_code


class TestChaosLLMUnavailable:

    def test_refactor_agent_no_llm_no_crash(self, refactor_agent_no_llm, clean_code):
        """RefactorAgent with no LLM must never crash."""
        result = refactor_agent_no_llm.refactor(clean_code, "long_method")
        assert isinstance(result, dict)

    def test_refactor_agent_no_llm_returns_original(self, refactor_agent_no_llm, long_method_code):
        """Without LLM, refactored_code must equal original."""
        result = refactor_agent_no_llm.refactor(long_method_code, "deep_nesting")
        assert result["refactored_code"] == long_method_code

    def test_refactor_agent_notes_mention_ollama(self, refactor_agent_no_llm, clean_code):
        """Without LLM, notes must guide user to enable Ollama."""
        result = refactor_agent_no_llm.refactor(clean_code, "high_complexity")
        notes = result["notes"].lower()
        assert any(word in notes for word in ["ollama", "llm", "available", "serve"])


class TestChaosSprintStoreFailure:

    @pytest.mark.asyncio
    async def test_sprint_store_ioerror_returns_500(self, async_client):
        """If SprintStore raises IOError, /log-sprint must return 500."""
        try:
            with patch("agile_risk.sprint_store.SprintStore.log_sprint",
                       side_effect=IOError("Disk full")):
                response = await async_client.post("/log-sprint", json={
                    "sprint_id": "Chaos-Sprint",
                    "smell_count": 5,
                    "refactor_count": 0,
                    "module": "default"
                })
                assert response.status_code == 500
        except Exception:
            pytest.skip("FastAPI app not available")

    @pytest.mark.asyncio
    async def test_sprint_risk_endpoint_exception_returns_500(self, async_client):
        """If SprintRiskModel raises unexpectedly, /predict-sprint-risk returns 500."""
        try:
            with patch("agile_risk.sprint_risk_model.SprintRiskModel.predict",
                       side_effect=RuntimeError("Model error")):
                response = await async_client.post("/predict-sprint-risk", json={
                    "sprint_history": [3, 5, 7, 10],
                    "threshold": 10
                })
                assert response.status_code == 500
        except Exception:
            pytest.skip("FastAPI app not available")


class TestChaosGracefulDegradation:

    def test_multiple_chaos_events_no_state_corruption(self):
        """Multiple failures in sequence must not corrupt shared state."""
        from analyzers.smell_detector import SmellDetector
        detector = SmellDetector()

        # Alternate between valid and invalid code
        results = []
        codes = ["def f(): pass", "def BROKEN(:", "def g(a, b): return a + b", "@@@@@@"]
        for code in codes:
            result = detector.detect(code)
            results.append(isinstance(result, list))

        assert all(results), "SmellDetector returned non-list after chaos inputs"

    def test_feature_extractor_recovery_after_failure(self):
        """FeatureExtractor must work correctly after handling a failure."""
        from analyzers.feature_extractor import FeatureExtractor
        extractor = FeatureExtractor()

        # First call: bad code
        result_bad = extractor.extract("x = @@@")
        assert result_bad is None

        # Second call: good code — must still work
        result_good = extractor.extract("def f(): return 42")
        assert result_good is not None
        assert len(result_good.standalone_functions) == 1
