"""Tests for data_loader module."""

import os
import tempfile

import pandas as pd
import pytest

from src.config import EXPECTED_FEATURES, TARGET_COLUMN
from src.data_loader import get_data_summary, load_csv, validate_columns


def _make_temp_csv(rows: int = 5) -> str:
    """Helper: create a minimal valid CSV with expected features + target, return path."""
    df = pd.DataFrame({col: [0] * rows for col in EXPECTED_FEATURES + [TARGET_COLUMN]})
    # Use a temp file that we manage — pytest tmp_path would work but here we
    # keep it explicit so load_csv only sees a real filesystem path.
    path = tempfile.mktemp(suffix=".csv")
    df.to_csv(path, index=False)
    return path


class TestLoadCsv:
    def test_loads_valid_csv(self):
        path = _make_temp_csv()
        try:
            df = load_csv(path)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 5
            assert all(col in df.columns for col in EXPECTED_FEATURES)
        finally:
            os.remove(path)

    def test_raises_file_not_found_for_missing_path(self):
        with pytest.raises(FileNotFoundError, match="数据文件不存在"):
            load_csv("/nonexistent/path.csv")


class TestValidateColumns:
    def test_returns_empty_list_when_all_columns_present(self):
        df = pd.DataFrame({col: [] for col in EXPECTED_FEATURES + [TARGET_COLUMN]})
        assert validate_columns(df) == []

    def test_reports_missing_target_column(self):
        df = pd.DataFrame({col: [] for col in EXPECTED_FEATURES})  # no target
        missing = validate_columns(df)
        assert TARGET_COLUMN in missing

    def test_reports_missing_feature_column(self):
        cols = [c for c in EXPECTED_FEATURES if c != "age"] + [TARGET_COLUMN]
        df = pd.DataFrame({col: [] for col in cols})
        missing = validate_columns(df)
        assert "age" in missing


class TestGetDataSummary:
    def test_returns_correct_row_count(self):
        df = pd.DataFrame({"age": [30, 45], TARGET_COLUMN: ["no", "yes"]})
        summary = get_data_summary(df)
        assert summary["rows"] == 2

    def test_returns_correct_column_count(self):
        df = pd.DataFrame({"age": [30], TARGET_COLUMN: ["no"]})
        summary = get_data_summary(df)
        assert summary["columns"] == 2

    def test_reports_missing_values(self):
        df = pd.DataFrame({"age": [30, None], TARGET_COLUMN: ["no", "yes"]})
        summary = get_data_summary(df)
        assert summary["missing"]["age"] == 1
        assert summary["missing"][TARGET_COLUMN] == 0

    def test_reports_dtypes(self):
        df = pd.DataFrame({"age": [30], TARGET_COLUMN: ["no"]})
        summary = get_data_summary(df)
        assert "int" in summary["dtypes"]["age"]
        assert "object" in summary["dtypes"][TARGET_COLUMN]
