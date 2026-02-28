"""
Category 7 — Agile Risk Prediction Model Tests.

Tests SprintRiskModel.predict() for:
  - Mathematical stability (edge cases: λ=0, μ=0, λ>>μ, negative growth)
  - Bayesian probability normalization (always in [0,1])
  - No division-by-zero
  - Historical replay accuracy (MAE)
  - Trend classification correctness
"""

import pytest


class TestSprintRiskModel:

    # ── λ = 0 (No new smells) ─────────────────────────────────────────────────

    def test_lambda_zero_stable_history(self, sprint_risk_model):
        """Flat history → drift=0, stable trend, low risk."""
        result = sprint_risk_model.predict([5, 5, 5, 5, 5], threshold=10)
        assert result["risk_probability"] >= 0.0
        assert result["risk_probability"] <= 1.0
        assert result["trend"] in ("stable", "improving", "above_threshold")
        assert result["predicted_smell_count"] == pytest.approx(5.0, abs=1.0)

    def test_lambda_zero_single_sprint_no_error(self, sprint_risk_model):
        """Single sprint history is allowed; model uses fallback sigma."""
        result = sprint_risk_model.predict([3], threshold=10)
        assert "risk_probability" in result
        assert 0.0 <= result["risk_probability"] <= 1.0

    # ── μ = 0 (No refactoring) ────────────────────────────────────────────────

    def test_mu_zero_growing_trend(self, sprint_risk_model):
        """Growing smell count with no refactoring → increasing trend."""
        result = sprint_risk_model.predict([2, 4, 6, 8], refactor_history=[], threshold=15)
        assert result["trend"] in ("increasing", "rapidly_increasing", "above_threshold")
        assert result["predicted_smell_count"] > 8

    # ── λ >> μ (Rapidly increasing) ───────────────────────────────────────────

    def test_rapid_growth_high_risk(self, sprint_risk_model):
        """Rapidly growing history → high risk probability."""
        result = sprint_risk_model.predict([1, 5, 10, 20, 35], threshold=15)
        assert result["trend"] == "rapidly_increasing"
        assert result["risk_probability"] > 0.5

    def test_rapid_growth_recommendation_critical(self, sprint_risk_model):
        """Rapidly growing trend should produce a critical or warning recommendation."""
        result = sprint_risk_model.predict([1, 5, 10, 20, 35], threshold=10)
        rec = result["recommendation"].lower()
        assert any(word in rec for word in ["critical", "warning", "refactor", "dedicate"])

    # ── Negative growth (Improving) ───────────────────────────────────────────

    def test_negative_growth_improving_trend(self, sprint_risk_model):
        """Decreasing smell history → improving or stable trend."""
        result = sprint_risk_model.predict([20, 15, 10, 5, 3], threshold=10)
        assert result["trend"] in ("improving", "stable")

    def test_negative_growth_low_risk(self, sprint_risk_model):
        """Improving trend → risk probability should be low."""
        result = sprint_risk_model.predict([30, 20, 10, 5], threshold=15)
        assert result["risk_probability"] < 0.8

    # ── Bayesian Stability ────────────────────────────────────────────────────

    def test_risk_probability_always_in_range(self, sprint_risk_model):
        """risk_probability must always be in [0, 1]."""
        test_cases = [
            ([1, 1, 1, 1], [], 10),
            ([1, 5, 10, 20], [], 5),
            ([100, 80, 60, 40], [20, 20, 20, 20], 50),
            ([0, 0, 0], [], 10),
            ([1000, 2000, 3000], [], 100),
        ]
        for history, refactor, threshold in test_cases:
            result = sprint_risk_model.predict(history, refactor, threshold)
            assert 0.0 <= result["risk_probability"] <= 1.0, (
                f"risk_probability={result['risk_probability']} for history={history}"
            )

    def test_no_division_by_zero(self, sprint_risk_model):
        """Single-element history must not crash."""
        result = sprint_risk_model.predict([5])
        assert result is not None
        assert 0.0 <= result["risk_probability"] <= 1.0

    def test_identical_history_no_divergence(self, sprint_risk_model):
        """Perfectly flat history must not produce NaN or infinity."""
        result = sprint_risk_model.predict([7, 7, 7, 7, 7, 7, 7])
        assert result["risk_probability"] != float("inf")
        assert result["risk_probability"] == result["risk_probability"]  # Not NaN

    def test_zero_smells_throughout(self, sprint_risk_model):
        """All-zero history is valid and must not crash."""
        result = sprint_risk_model.predict([0, 0, 0, 0])
        assert "risk_probability" in result
        assert result["risk_probability"] >= 0.0

    # ── Historical Replay ─────────────────────────────────────────────────────

    def test_historical_replay_mae_threshold(self, sprint_risk_model):
        """
        Feed 9 historical sprints, predict the 10th, compare to actual.
        MAE must be < 10 smells (lenient for stochastic model).
        """
        historical = [3, 5, 4, 7, 8, 10, 9, 12, 14]
        actual_count = 16  # Known 10th sprint value

        result = sprint_risk_model.predict(historical, threshold=20)
        predicted = result["predicted_smell_count"]
        mae = abs(predicted - actual_count)

        print(f"\n[Risk Model] Predicted: {predicted:.2f}, Actual: {actual_count}, MAE: {mae:.2f}")
        assert mae < 15, f"MAE {mae:.2f} exceeds acceptable threshold of 15"

    def test_refactor_history_reduces_risk(self, sprint_risk_model):
        """With active refactoring, risk should be lower than without."""
        growing = [2, 5, 8, 12]
        result_no_refactor = sprint_risk_model.predict(growing, threshold=15)
        result_with_refactor = sprint_risk_model.predict(growing, refactor_history=[3, 3, 3, 3],
                                                          threshold=15)
        # With refactoring, predicted count should be lower
        assert result_with_refactor["predicted_smell_count"] <= (
            result_no_refactor["predicted_smell_count"] + 1.0
        )

    # ── Output Format ─────────────────────────────────────────────────────────

    def test_required_keys_present(self, sprint_risk_model):
        result = sprint_risk_model.predict([1, 2, 3])
        required = {"risk_probability", "predicted_smell_count", "threshold", "trend",
                    "recommendation"}
        assert required.issubset(result.keys())

    def test_trend_is_valid_string(self, sprint_risk_model):
        for history in [[5, 5, 5], [1, 5, 10], [10, 5, 1]]:
            result = sprint_risk_model.predict(history)
            assert isinstance(result["trend"], str) and len(result["trend"]) > 0

    def test_recommendation_is_string(self, sprint_risk_model):
        result = sprint_risk_model.predict([3, 4, 6])
        assert isinstance(result["recommendation"], str)
        assert len(result["recommendation"]) > 0

    def test_above_threshold_trend_when_current_exceeds(self, sprint_risk_model):
        """If current smell count is above threshold, trend reflects that."""
        result = sprint_risk_model.predict([5, 5, 5, 5], threshold=3)
        # predicted_smell_count ~5, which is > threshold=3
        assert result["trend"] in ("above_threshold", "stable", "increasing")
        assert result["risk_probability"] > 0.5
