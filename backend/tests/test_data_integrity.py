"""
Category 10 — Data Integrity Tests.

Tests SprintStore for:
  - Correct persistence and retrieval using real API
  - JSON file validity after writes
  - SmellDetector and FeatureExtractor handle invalid code safely
"""

import json
import os
import pytest
from unittest.mock import patch
from pathlib import Path


class TestDataIntegrity:

    @pytest.fixture
    def temp_store(self, tmp_path, monkeypatch):
        """SprintStore using a temp file instead of the real sprint_data.json."""
        store_file = tmp_path / "sprint_data.json"
        store_file.write_text(json.dumps({"sprints": []}, indent=2))

        import agile_risk.sprint_store as ss_module
        monkeypatch.setattr(ss_module, "_DATA_FILE", store_file)

        from agile_risk.sprint_store import SprintStore
        store = SprintStore()
        return store

    # ── Persistence ────────────────────────────────────────────────────────────

    def test_log_and_retrieve_sprint(self, temp_store):
        temp_store.log_sprint("Sprint-1", smell_count=5, refactor_count=2)
        data = temp_store.get_all()
        sprint_ids = [s["sprint_id"] for s in data["sprints"]]
        assert "Sprint-1" in sprint_ids

    def test_logged_data_fields_correct(self, temp_store):
        temp_store.log_sprint("Sprint-2", smell_count=8, refactor_count=3, module="auth")
        data = temp_store.get_all()
        sprint = next(s for s in data["sprints"] if s["sprint_id"] == "Sprint-2")
        assert sprint["smell_count"] == 8
        assert sprint["refactor_count"] == 3
        assert sprint["module"] == "auth"

    def test_multiple_sprints_all_stored(self, temp_store):
        for i in range(5):
            temp_store.log_sprint(f"Sprint-{i}", smell_count=i * 2, refactor_count=i)
        data = temp_store.get_all()
        assert data["summary"]["total_sprints"] == 5

    def test_smell_history_list_correct(self, temp_store):
        counts = [3, 5, 7, 10]
        for i, count in enumerate(counts):
            temp_store.log_sprint(f"S-{i}", smell_count=count)
        history = temp_store.get_smell_history()
        assert history == counts

    def test_refactor_history_list_correct(self, temp_store):
        refactors = [1, 2, 3]
        for i, r in enumerate(refactors):
            temp_store.log_sprint(f"S-{i}", smell_count=5, refactor_count=r)
        history = temp_store.get_refactor_history()
        assert history == refactors

    # ── File Validity ──────────────────────────────────────────────────────────

    def test_sprint_store_file_is_valid_json(self, temp_store, tmp_path):
        temp_store.log_sprint("Sprint-JSON", smell_count=4)
        import agile_risk.sprint_store as ss_module
        path = ss_module._DATA_FILE
        with open(path) as f:
            data = json.load(f)
        assert "sprints" in data
        assert isinstance(data["sprints"], list)

    def test_empty_store_summary_zero(self, temp_store):
        data = temp_store.get_all()
        assert data["summary"]["total_sprints"] == 0
        assert data["summary"]["total_smells_detected"] == 0

    # ── No Partial Writes ──────────────────────────────────────────────────────

    def test_store_file_always_valid_json_after_writes(self, temp_store, tmp_path):
        for i in range(10):
            temp_store.log_sprint(f"Sprint-{i}", smell_count=i)
        import agile_risk.sprint_store as ss_module
        path = ss_module._DATA_FILE
        with open(path) as f:
            parsed = json.loads(f.read())
        assert isinstance(parsed["sprints"], list)

    def test_repeated_sprint_id_handled_gracefully(self, temp_store):
        temp_store.log_sprint("Sprint-DUP", smell_count=3)
        temp_store.log_sprint("Sprint-DUP", smell_count=6)
        data = temp_store.get_all()
        dup_entries = [s for s in data["sprints"] if s["sprint_id"] == "Sprint-DUP"]
        assert len(dup_entries) >= 1

    # ── Component Error Safety ─────────────────────────────────────────────────

    def test_no_corrupted_data_returned_on_invalid_code(self):
        from analyzers.smell_detector import SmellDetector
        detector = SmellDetector()
        result = detector.detect("def broken(:\n    @@invalid@@")
        assert isinstance(result, list)
        assert result == []

    def test_feature_extractor_returns_none_on_invalid(self):
        from analyzers.feature_extractor import FeatureExtractor
        extractor = FeatureExtractor()
        result = extractor.extract("x = @@@")
        assert result is None

    def test_store_load_fallback_on_corrupt_file(self, tmp_path, monkeypatch):
        """If file is corrupted, _load() must return safe default."""
        store_file = tmp_path / "sprint_data.json"
        store_file.write_text("{{NOT VALID JSON}}")

        import agile_risk.sprint_store as ss_module
        monkeypatch.setattr(ss_module, "_DATA_FILE", store_file)

        from agile_risk.sprint_store import SprintStore
        store = SprintStore()
        result = store._load()
        assert isinstance(result, dict)
        assert "sprints" in result
