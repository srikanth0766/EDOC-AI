"""
Category 2 — Feature Extraction Validation.

Tests FeatureExtractor for correct computation of:
  - Cyclomatic Complexity
  - LOC (Lines of Code)
  - Nesting Depth
  - WMC (Weighted Methods per Class)
  - CBO (Coupling Between Objects)
  - Parameter Count (excluding self/cls)
"""

import pytest


class TestFeatureExtractor:

    # ── Cyclomatic Complexity ─────────────────────────────────────────────────

    def test_base_complexity_simple_function(self, feature_extractor):
        """Function with no branches → complexity = 1."""
        code = "def simple():\n    return 42\n"
        features = feature_extractor.extract(code)
        assert features is not None
        fn = features.standalone_functions[0]
        assert fn.complexity == 1

    def test_complexity_one_if(self, feature_extractor):
        """One if-branch adds 1 → complexity = 2."""
        code = "def f(a):\n    if a:\n        return 1\n    return 0\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.complexity == 2

    def test_complexity_two_ifs(self, feature_extractor):
        """Two independent ifs → complexity = 3."""
        code = "def f(a, b):\n    if a:\n        pass\n    if b:\n        pass\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.complexity == 3

    def test_complexity_if_for_while(self, feature_extractor):
        """if + for + while → base(1) + 3 = 4."""
        code = (
            "def f(a):\n"
            "    if a:\n"
            "        pass\n"
            "    for i in range(3):\n"
            "        pass\n"
            "    while a:\n"
            "        a -= 1\n"
        )
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.complexity >= 4

    def test_complexity_boolean_and(self, feature_extractor):
        """BoolOp 'and' with 2 values adds 1 branch."""
        code = "def f(a, b):\n    if a and b:\n        pass\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        # base=1 + if=1 + and=1 = 3
        assert fn.complexity >= 3

    # ── LOC ──────────────────────────────────────────────────────────────────

    def test_loc_excludes_blank_lines(self, feature_extractor):
        code = "def f():\n\n    x = 1\n\n    return x\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        # def, x=1, return → 3 non-blank lines
        assert fn.loc == 3

    def test_total_loc_counts_non_blank(self, feature_extractor):
        code = "x = 1\n\ny = 2\n\nz = 3\n"
        features = feature_extractor.extract(code)
        assert features.total_loc == 3

    # ── Parameter Count ───────────────────────────────────────────────────────

    def test_params_excludes_self(self, feature_extractor):
        code = "class C:\n    def method(self, a, b):\n        pass\n"
        features = feature_extractor.extract(code)
        method = features.classes[0].methods[0]
        assert method.params == 2  # 'a' and 'b', not 'self'

    def test_params_excludes_cls(self, feature_extractor):
        code = "class C:\n    @classmethod\n    def create(cls, x, y):\n        pass\n"
        features = feature_extractor.extract(code)
        method = features.classes[0].methods[0]
        assert method.params == 2  # 'x' and 'y', not 'cls'

    def test_params_zero_for_no_args(self, feature_extractor):
        code = "def no_args():\n    pass\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.params == 0

    def test_params_many(self, large_param_code, feature_extractor):
        features = feature_extractor.extract(large_param_code)
        fn = features.standalone_functions[0]
        assert fn.params == 7

    # ── Nesting Depth ─────────────────────────────────────────────────────────

    def test_nesting_depth_flat(self, feature_extractor):
        code = "def f():\n    x = 1\n    y = 2\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.max_nesting_depth == 0

    def test_nesting_depth_one_if(self, feature_extractor):
        code = "def f(a):\n    if a:\n        return 1\n"
        features = feature_extractor.extract(code)
        fn = features.standalone_functions[0]
        assert fn.max_nesting_depth == 1

    def test_nesting_depth_deep(self, deep_nesting_code, feature_extractor):
        features = feature_extractor.extract(deep_nesting_code)
        fn = features.standalone_functions[0]
        assert fn.max_nesting_depth >= 4

    # ── WMC ──────────────────────────────────────────────────────────────────

    def test_wmc_is_sum_of_method_complexities(self, feature_extractor):
        code = (
            "class MyClass:\n"
            "    def m1(self):\n"
            "        pass\n"
            "    def m2(self, a):\n"
            "        if a:\n"
            "            pass\n"
        )
        features = feature_extractor.extract(code)
        cls = features.classes[0]
        m1 = cls.methods[0]
        m2 = cls.methods[1]
        assert cls.wmc == m1.complexity + m2.complexity

    # ── CBO ──────────────────────────────────────────────────────────────────

    def test_cbo_zero_no_imports(self, feature_extractor):
        code = "class Pure:\n    def method(self):\n        return 42\n"
        features = feature_extractor.extract(code)
        cls = features.classes[0]
        assert cls.cbo == 0

    def test_cbo_increases_with_external_refs(self, feature_extractor):
        code = (
            "import os\n"
            "import sys\n"
            "class WithDeps:\n"
            "    def method(self):\n"
            "        os.getcwd()\n"
            "        sys.exit()\n"
        )
        features = feature_extractor.extract(code)
        cls = features.classes[0]
        assert cls.cbo >= 1

    # ── Imports ───────────────────────────────────────────────────────────────

    def test_imports_collected(self, feature_extractor):
        code = "import os\nimport sys\nfrom typing import List\nx = 1\n"
        features = feature_extractor.extract(code)
        assert "os" in features.imports
        assert "sys" in features.imports

    def test_invalid_code_returns_none(self, feature_extractor):
        features = feature_extractor.extract("def broken(:\n    pass")
        assert features is None

    # ── num_methods ───────────────────────────────────────────────────────────

    def test_num_methods_accuracy(self, god_class_code, feature_extractor):
        features = feature_extractor.extract(god_class_code)
        cls = features.classes[0]
        assert cls.num_methods == 12
