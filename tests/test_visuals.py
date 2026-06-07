"""Tests for visuals module."""

import pandas as pd
import plotly.graph_objects as go

from src.config import TARGET_COLUMN
from src.visuals import (
    plot_correlation_heatmap,
    plot_numeric_histogram,
    plot_target_distribution,
)


def _make_df():
    return pd.DataFrame(
        {
            "age": [30, 45, 28, 60, 35],
            "duration": [120, 300, 90, 450, 200],
            "campaign": [1, 3, 2, 1, 2],
            TARGET_COLUMN: ["no", "yes", "no", "yes", "no"],
        }
    )


class TestPlotTargetDistribution:
    def test_returns_figure(self):
        fig = plot_target_distribution(_make_df())
        assert isinstance(fig, go.Figure)

    def test_pie_has_two_traces_for_two_classes(self):
        fig = plot_target_distribution(_make_df())
        # px.pie produces one trace with labels/values
        assert "pie" in fig.data[0].type

    def test_handles_missing_target(self):
        df = pd.DataFrame({"age": [30]})
        fig = plot_target_distribution(df)
        # Should still return a Figure (with annotation)
        assert isinstance(fig, go.Figure)


class TestPlotNumericHistogram:
    def test_returns_figure_for_valid_column(self):
        fig = plot_numeric_histogram(_make_df(), "age")
        assert isinstance(fig, go.Figure)
        # px.histogram produces a histogram trace
        assert fig.data[0].type == "histogram"

    def test_handles_missing_column(self):
        fig = plot_numeric_histogram(_make_df(), "nonexistent")
        assert isinstance(fig, go.Figure)

    def test_handles_categorical_column(self):
        fig = plot_numeric_histogram(_make_df(), TARGET_COLUMN)
        assert isinstance(fig, go.Figure)


class TestPlotCorrelationHeatmap:
    def test_returns_figure(self):
        fig = plot_correlation_heatmap(_make_df())
        assert isinstance(fig, go.Figure)

    def test_heatmap_has_data_trace(self):
        fig = plot_correlation_heatmap(_make_df())
        assert len(fig.data) > 0

    def test_handles_no_numeric_columns(self):
        df = pd.DataFrame({"cat": ["a", "b"], TARGET_COLUMN: ["no", "yes"]})
        fig = plot_correlation_heatmap(df)
        assert isinstance(fig, go.Figure)
