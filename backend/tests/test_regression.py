"""
Category 13 — Regression Suite.

Runs smell detector against curated fixture files with known expected outputs.
Each fixture has a expected_smell (or None for clean code).
"""

import os
import pytest


# ─── Regression Cases ────────────────────────────────────────────────────────
# (fixture_filename, expected_smell_or_None, min_expected_count)
REGRESSION_CASES = [
    ("clean_class.py",          None,              0),
    ("god_class_sample.py",     "god_class",       1),
    ("long_method_sample.py",   "long_method",     1),
    ("deep_nesting_sample.py",  "deep_nesting",    1),
    ("high_complexity_sample.py", "high_complexity", 1),
]

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(filename: str) -> str:
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "r") as f:
        return f.read()


class TestRegression:

    @pytest.fixture
    def smell_detector(self):
        from analyzers.smell_detector import SmellDetector
        return SmellDetector()

    @pytest.mark.parametrize("filename,expected_smell,min_count", REGRESSION_CASES)
    def test_regression_fixture(self, smell_detector, filename, expected_smell, min_count):
        """Parametrized regression: each fixture must match expected smell output."""
        code = load_fixture(filename)
        smells = smell_detector.detect(code)
        smell_names = [s.smell for s in smells]

        if expected_smell is None:
            assert len(smells) == 0, (
                f"REGRESSION: {filename} should be clean but got: {smell_names}"
            )
        else:
            assert expected_smell in smell_names, (
                f"REGRESSION: {filename} expected '{expected_smell}' "
                f"but only found: {smell_names}"
            )
            matching = [s for s in smells if s.smell == expected_smell]
            assert len(matching) >= min_count

    @pytest.mark.parametrize("filename,expected_smell,_", REGRESSION_CASES)
    def test_regression_output_stable(self, smell_detector, filename, expected_smell, _):
        """Same fixture analyzed twice must produce identical results."""
        code = load_fixture(filename)
        result1 = [s.smell for s in smell_detector.detect(code)]
        result2 = [s.smell for s in smell_detector.detect(code)]
        assert result1 == result2, (
            f"REGRESSION: {filename} produces unstable results: {result1} vs {result2}"
        )

    @pytest.mark.parametrize("filename,expected_smell,_", REGRESSION_CASES)
    def test_regression_confidence_stable(self, smell_detector, filename, expected_smell, _):
        """Confidence scores must be identical between two calls."""
        code = load_fixture(filename)
        conf1 = [round(s.confidence, 4) for s in smell_detector.detect(code)]
        conf2 = [round(s.confidence, 4) for s in smell_detector.detect(code)]
        assert conf1 == conf2

    def test_all_fixtures_exist(self):
        """Verify all expected fixture files are present."""
        for filename, _, _ in REGRESSION_CASES:
            path = os.path.join(FIXTURES_DIR, filename)
            assert os.path.exists(path), f"Fixture file missing: {filename}"

    def test_clean_class_zero_smells(self, smell_detector):
        """clean_class.py must produce exactly 0 smells."""
        code = load_fixture("clean_class.py")
        smells = smell_detector.detect(code)
        assert len(smells) == 0

    def test_god_class_metric_value_correct(self, smell_detector):
        """god_class_sample: metric_value must be >= 12 (12 methods)."""
        code = load_fixture("god_class_sample.py")
        smells = smell_detector.detect(code)
        gc = next((s for s in smells if s.smell == "god_class"), None)
        assert gc is not None
        assert gc.metric_value >= 12

    def test_long_method_loc_over_threshold(self, smell_detector):
        """long_method_sample: metric_value must be > 30 (threshold)."""
        code = load_fixture("long_method_sample.py")
        smells = smell_detector.detect(code)
        lm = next((s for s in smells if s.smell == "long_method"), None)
        assert lm is not None
        assert lm.metric_value > 30

    def test_deep_nesting_depth_correct(self, smell_detector):
        """deep_nesting_sample: metric_value must be >= 4."""
        code = load_fixture("deep_nesting_sample.py")
        smells = smell_detector.detect(code)
        dn = next((s for s in smells if s.smell == "deep_nesting"), None)
        assert dn is not None
        assert dn.metric_value >= 4
