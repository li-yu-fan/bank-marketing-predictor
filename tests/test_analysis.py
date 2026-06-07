"""Tests for analysis module."""

import pandas as pd

from src.analysis import (
    get_correlation_matrix,
    get_missing_summary,
    get_numeric_stats,
    get_target_distribution,
)
from src.config import TARGET_COLUMN


def _make_sample_df() -> pd.DataFrame:
    """Return a small DataFrame with numeric and categorical columns + target."""
    return pd.DataFrame(
        {
            "age": [30, 45, 28, 60],
            "job": ["admin", "blue-collar", "admin", "retired"],
            "duration": [120, 300, 90, 450],
            "campaign": [1, 3, 2, 1],
            TARGET_COLUMN: ["no", "yes", "no", "yes"],
        }
    )


class TestGetNumericStats:
    def test_returns_describe_for_numeric_columns(self):
        df = _make_sample_df()
        stats = get_numeric_stats(df)
        assert "age" in stats.columns
        assert "duration" in stats.columns
        assert "campaign" in stats.columns
        # job is categorical, should not be in describe
        assert "job" not in stats.columns

    def test_returns_correct_mean(self):
        df = pd.DataFrame({"age": [30, 40, 50]})
        stats = get_numeric_stats(df)
        assert stats.loc["mean", "age"] == 40.0


class TestGetTargetDistribution:
    def test_returns_correct_counts(self):
        df = _make_sample_df()
        result = get_target_distribution(df)
        assert result["counts"] == {"no": 2, "yes": 2}
        assert result["total"] == 4

    def test_returns_correct_proportions(self):
        df = _make_sample_df()
        result = get_target_distribution(df)
        assert result["proportions"]["no"] == 0.5
        assert result["proportions"]["yes"] == 0.5

    def test_returns_empty_dict_when_target_missing(self):
        df = pd.DataFrame({"age": [30]})
        assert get_target_distribution(df) == {}

    def test_handles_empty_dataframe(self):
        df = pd.DataFrame({TARGET_COLUMN: []})
        result = get_target_distribution(df)
        assert result["total"] == 0
        assert result["counts"] == {}


class TestGetCorrelationMatrix:
    def test_returns_correlation_dataframe(self):
        df = _make_sample_df()
        corr = get_correlation_matrix(df)
        # Diagonal should be 1.0 (self-correlation)
        assert corr.loc["age", "age"] == 1.0
        assert corr.loc["duration", "duration"] == 1.0

    def test_correlation_is_symmetric(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        corr = get_correlation_matrix(df)
        assert corr.loc["a", "b"] == corr.loc["b", "a"]


class TestGetMissingSummary:
    def test_returns_empty_df_when_no_missing(self):
        df = pd.DataFrame({"age": [30, 45], TARGET_COLUMN: ["no", "yes"]})
        result = get_missing_summary(df)
        assert len(result) == 0

    def test_reports_missing_count_and_pct(self):
        df = pd.DataFrame(
            {"age": [30, None, None, 60], TARGET_COLUMN: ["no", "yes", "no", "yes"]}
        )
        result = get_missing_summary(df)
        assert result.loc[0, "column"] == "age"
        assert result.loc[0, "missing_count"] == 2
        assert result.loc[0, "missing_pct"] == 50.0

    def test_handles_all_missing(self):
        df = pd.DataFrame({"age": [None, None]})
        result = get_missing_summary(df)
        assert result.loc[0, "missing_pct"] == 100.0
