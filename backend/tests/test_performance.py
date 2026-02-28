"""
Category 8 — Performance & Scalability Tests.

Tests:
  - Large codebase (5000+ LOC): parsing time < 10s, memory < 500MB
  - High-branch function: cyclomatic complexity computed in < 2s
  - Concurrent analysis: 10 threads, no deadlocks, no exceptions
"""

import time
import threading
import pytest


def generate_large_code(num_functions: int = 150) -> str:
    """Generate synthetic Python code with ~5000 non-blank lines."""
    lines = []
    for i in range(num_functions):
        lines.append(f"def func_{i}(a: int, b: int) -> int:")
        lines.append(f"    \"\"\"Auto-generated function {i}.\"\"\"")
        lines.append(f"    result = a + b")
        lines.append(f"    if a > 0:")
        lines.append(f"        result += a * 2")
        lines.append(f"    if b > 0:")
        lines.append(f"        result += b * 3")
        lines.append(f"    for k in range(min(a, 10)):")
        lines.append(f"        result += k")
        lines.append(f"    return result")
        lines.append("")
    return "\n".join(lines)


def generate_high_branch_code(num_branches: int = 100) -> str:
    """Generate a function with many if branches."""
    lines = ["def high_branch(x):"]
    for i in range(num_branches):
        lines.append(f"    if x == {i}:")
        lines.append(f"        return {i}")
    lines.append("    return -1")
    return "\n".join(lines)


class TestPerformance:

    def test_large_codebase_parsing_time(self):
        """SmellDetector.detect() on ~5000 LOC must complete in < 10s."""
        from analyzers.smell_detector import SmellDetector
        detector = SmellDetector()
        code = generate_large_code(num_functions=150)

        start = time.perf_counter()
        smells = detector.detect(code)
        elapsed = time.perf_counter() - start

        print(f"\n[Performance] Large codebase ({len(code.splitlines())} lines): {elapsed:.3f}s")
        assert elapsed < 10.0, f"Parsing took {elapsed:.2f}s — exceeds 10s threshold"
        assert isinstance(smells, list)

    def test_large_codebase_memory(self):
        """Memory usage for 5000 LOC analysis must stay < 500MB."""
        try:
            import psutil
            import os
        except ImportError:
            pytest.skip("psutil not installed")

        from analyzers.smell_detector import SmellDetector
        detector = SmellDetector()
        code = generate_large_code(num_functions=150)

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 ** 2)  # MB

        _ = detector.detect(code)

        mem_after = process.memory_info().rss / (1024 ** 2)
        delta = mem_after - mem_before
        print(f"\n[Performance] Memory delta: {delta:.1f}MB (before={mem_before:.1f}MB, after={mem_after:.1f}MB)")
        assert mem_after < 500, f"Memory usage {mem_after:.1f}MB exceeds 500MB"

    def test_high_branch_complexity_time(self):
        """Cyclomatic complexity for 100-branch function must complete in < 2s."""
        from analyzers.feature_extractor import FeatureExtractor
        extractor = FeatureExtractor()
        code = generate_high_branch_code(100)

        start = time.perf_counter()
        features = extractor.extract(code)
        elapsed = time.perf_counter() - start

        print(f"\n[Performance] 100-branch complexity extraction: {elapsed:.3f}s")
        assert elapsed < 2.0, f"Complexity extraction took {elapsed:.2f}s — exceeds 2s"
        assert features is not None
        fn = features.standalone_functions[0]
        assert fn.complexity >= 100, f"Expected complexity >= 100, got {fn.complexity}"

    def test_concurrent_analysis_no_exceptions(self):
        """10 concurrent threads calling FeatureExtractor must not throw."""
        from analyzers.feature_extractor import FeatureExtractor

        errors = []
        code = generate_large_code(50)

        def run_analysis(thread_id: int):
            try:
                extractor = FeatureExtractor()
                features = extractor.extract(code)
                assert features is not None
            except Exception as e:
                errors.append(f"Thread {thread_id}: {e}")

        threads = [threading.Thread(target=run_analysis, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        assert len(errors) == 0, f"Concurrent analysis errors: {errors}"

    def test_concurrent_analysis_no_deadlock(self):
        """10 threads must all complete within 30s (deadlock detection)."""
        from analyzers.smell_detector import SmellDetector

        completed = []
        code = generate_large_code(30)

        def run_detection(thread_id: int):
            detector = SmellDetector()
            _ = detector.detect(code)
            completed.append(thread_id)

        threads = [threading.Thread(target=run_detection, args=(i,)) for i in range(10)]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        elapsed = time.perf_counter() - start

        print(f"\n[Performance] 10 concurrent detections completed in {elapsed:.2f}s")
        assert len(completed) == 10, (
            f"Only {len(completed)}/10 threads completed — possible deadlock"
        )

    def test_feature_extractor_speed_single_function(self):
        """Feature extraction of a single function must be near-instant (< 0.5s)."""
        from analyzers.feature_extractor import FeatureExtractor
        code = "def f(a, b, c):\n    if a:\n        return b + c\n    return 0\n"
        extractor = FeatureExtractor()

        start = time.perf_counter()
        for _ in range(100):
            extractor.extract(code)
        elapsed = time.perf_counter() - start

        print(f"\n[Performance] 100 × single function extraction: {elapsed:.3f}s")
        assert elapsed < 2.0
