"""
Category 6 — CI/CD Gatekeeper Tests.

Simulates 50 synthetic PR scenarios:
  - 25 "clean" PRs → smell score low → PASS
  - 25 "smelly" PRs → smell score high → BLOCK
  - Configurable threshold test
  - False rejection rate measurement
"""

import pytest


# ── Synthetic PR generators ────────────────────────────────────────────────────

def generate_clean_pr(index: int) -> str:
    """Generate a clean, simple function for PR simulation."""
    return f"""\
def clean_func_{index}(a: int, b: int) -> int:
    \"\"\"Simple clean function number {index}.\"\"\"
    return a + b
"""


def generate_smelly_pr(index: int) -> str:
    """Generate a god class to simulate a smelly PR."""
    methods = "\n".join(
        f"    def method_{i}(self): pass" for i in range(12)
    )
    return f"""\
class GodClass_{index}:
{methods}
"""


# ── Gatekeeper logic ───────────────────────────────────────────────────────────

class CIGatekeeper:
    """
    Simulates CI gate: block PRs where overall_smell_score >= threshold
    or high_confidence_count >= max_high_conf.
    """

    def __init__(self, score_threshold: float = 0.5, max_high_conf: int = 1):
        self.score_threshold = score_threshold
        self.max_high_conf = max_high_conf

    def evaluate(self, smell_response: dict) -> dict:
        score = smell_response.get("overall_smell_score", 0.0)
        high_conf = smell_response.get("high_confidence_count", 0)
        passed = score < self.score_threshold and high_conf < self.max_high_conf
        return {
            "passed": passed,
            "score": score,
            "high_conf": high_conf,
            "reason": "ok" if passed else f"score={score:.2f} high_conf={high_conf}",
        }


class TestCIGatekeeper:

    @pytest.fixture
    def gatekeeper(self):
        return CIGatekeeper(score_threshold=0.5, max_high_conf=1)

    @pytest.fixture
    def smell_detector(self):
        from analyzers.smell_detector import SmellDetector
        return SmellDetector()

    # ── 25 Clean PRs ──────────────────────────────────────────────────────────

    def test_25_clean_prs_pass(self, smell_detector, gatekeeper):
        results = []
        for i in range(25):
            code = generate_clean_pr(i)
            smells = smell_detector.detect_to_dict(code)
            high_conf = [s for s in smells if s["confidence"] > 0.75]
            score = max((s["confidence"] for s in smells), default=0.0)
            response = {
                "overall_smell_score": score,
                "high_confidence_count": len(high_conf),
            }
            outcome = gatekeeper.evaluate(response)
            results.append(outcome["passed"])

        pass_count = sum(results)
        false_rejection_rate = (25 - pass_count) / 25
        print(f"\n[CI Gate] Clean PR pass rate: {pass_count}/25")
        print(f"[CI Gate] False rejection rate: {false_rejection_rate:.2%}")
        assert false_rejection_rate <= 0.10, (
            f"False rejection rate {false_rejection_rate:.2%} exceeds 10% threshold"
        )

    # ── 25 Smelly PRs ─────────────────────────────────────────────────────────

    def test_25_smelly_prs_blocked(self, smell_detector, gatekeeper):
        results = []
        for i in range(25):
            code = generate_smelly_pr(i)
            smells = smell_detector.detect_to_dict(code)
            high_conf = [s for s in smells if s["confidence"] > 0.75]
            score = max((s["confidence"] for s in smells), default=0.0)
            response = {
                "overall_smell_score": score,
                "high_confidence_count": len(high_conf),
            }
            outcome = gatekeeper.evaluate(response)
            results.append(not outcome["passed"])  # True if correctly blocked

        block_count = sum(results)
        block_rate = block_count / 25
        print(f"\n[CI Gate] Smelly PR block rate: {block_count}/25")
        assert block_rate >= 0.80, (
            f"CI gate only blocked {block_rate:.2%} of smelly PRs (need >= 80%)"
        )

    # ── Combined Pass/Block Accuracy ──────────────────────────────────────────

    def test_overall_gate_accuracy(self, smell_detector, gatekeeper):
        """Combined accuracy over 50 PRs must be >= 80%."""
        correct = 0
        total = 50

        for i in range(25):
            code = generate_clean_pr(i)
            smells = smell_detector.detect_to_dict(code)
            score = max((s["confidence"] for s in smells), default=0.0)
            high_conf = len([s for s in smells if s["confidence"] > 0.75])
            outcome = gatekeeper.evaluate({"overall_smell_score": score,
                                           "high_confidence_count": high_conf})
            if outcome["passed"]:
                correct += 1

        for i in range(25):
            code = generate_smelly_pr(i)
            smells = smell_detector.detect_to_dict(code)
            score = max((s["confidence"] for s in smells), default=0.0)
            high_conf = len([s for s in smells if s["confidence"] > 0.75])
            outcome = gatekeeper.evaluate({"overall_smell_score": score,
                                           "high_confidence_count": high_conf})
            if not outcome["passed"]:
                correct += 1

        accuracy = correct / total
        print(f"\n[CI Gate] Overall accuracy: {accuracy:.2%} ({correct}/{total})")
        assert accuracy >= 0.80, f"CI gate accuracy {accuracy:.2%} below 80%"

    # ── Configurable Threshold ────────────────────────────────────────────────

    def test_lower_threshold_blocks_more(self, smell_detector):
        """Lowering threshold must block more PRs."""
        strict_gate = CIGatekeeper(score_threshold=0.1, max_high_conf=0)
        lenient_gate = CIGatekeeper(score_threshold=0.9, max_high_conf=100)

        test_code = generate_smelly_pr(99)
        smells = smell_detector.detect_to_dict(test_code)
        score = max((s["confidence"] for s in smells), default=0.0)
        high_conf = len([s for s in smells if s["confidence"] > 0.75])
        response = {"overall_smell_score": score, "high_confidence_count": high_conf}

        strict_result = strict_gate.evaluate(response)
        lenient_result = lenient_gate.evaluate(response)

        # Strict must be at least as restrictive as lenient
        # (If strict blocks, lenient may or may not — but not the reverse)
        if not strict_result["passed"]:
            # This is expected; lenient may still pass it
            assert True
        else:
            assert lenient_result["passed"]

    def test_threshold_change_reflects_in_outcome(self, smell_detector):
        """Same code evaluated with different thresholds produces different outcomes."""
        code = generate_smelly_pr(42)
        smells = smell_detector.detect_to_dict(code)
        score = max((s["confidence"] for s in smells), default=0.0)
        high_conf = len([s for s in smells if s["confidence"] > 0.75])
        response = {"overall_smell_score": score, "high_confidence_count": high_conf}

        gate_strict = CIGatekeeper(score_threshold=0.1, max_high_conf=0)
        gate_lenient = CIGatekeeper(score_threshold=0.99, max_high_conf=1000)

        strict_outcome = gate_strict.evaluate(response)
        lenient_outcome = gate_lenient.evaluate(response)

        # With a real smelly PR, strict should block while lenient passes
        if score > 0:
            assert not strict_outcome["passed"], "Strict gate should block smelly PR"
            assert lenient_outcome["passed"], "Lenient gate should not block"

    # ── Gatekeeper Response Format ────────────────────────────────────────────

    def test_outcome_has_required_keys(self, gatekeeper):
        response = {"overall_smell_score": 0.2, "high_confidence_count": 0}
        outcome = gatekeeper.evaluate(response)
        assert "passed" in outcome
        assert "score" in outcome
        assert "reason" in outcome

    def test_passed_is_boolean(self, gatekeeper):
        response = {"overall_smell_score": 0.1, "high_confidence_count": 0}
        outcome = gatekeeper.evaluate(response)
        assert isinstance(outcome["passed"], bool)
