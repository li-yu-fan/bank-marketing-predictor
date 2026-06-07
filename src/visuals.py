"""Plotly chart builders for Bank Marketing data — pure functions returning Figure."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import TARGET_COLUMN


def plot_target_distribution(df: pd.DataFrame) -> go.Figure:
    """Pie chart showing class balance of the target column."""
    if TARGET_COLUMN not in df.columns:
        return _empty_figure("目标列不存在")
    counts = df[TARGET_COLUMN].value_counts().reset_index()
    counts.columns = ["subscription", "count"]
    return px.pie(
        counts,
        names="subscription",
        values="count",
        title="认购分布 (Subscription Distribution)",
        color="subscription",
        color_discrete_map={"yes": "#2ca02c", "no": "#d62728"},
    )


def plot_numeric_histogram(df: pd.DataFrame, column: str) -> go.Figure:
    """Histogram for a single numeric column."""
    if column not in df.columns:
        return _empty_figure(f"列 '{column}' 不存在")
    if not pd.api.types.is_numeric_dtype(df[column]):
        return _empty_figure(f"列 '{column}' 不是数值型")
    return px.histogram(
        df,
        x=column,
        nbins=30,
        title=f"{column} 分布",
        marginal="box",
    )


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Correlation heatmap for numeric columns."""
    corr = df.corr(numeric_only=True)
    if corr.empty:
        return _empty_figure("没有数值列可计算相关性")
    # Mask the upper triangle to avoid duplicate info
    mask = _upper_triangle_mask(corr)
    fig = px.imshow(
        mask,
        text_auto=".2f",
        title="相关性热力图 (Correlation Heatmap)",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
    )
    fig.update_layout(coloraxis_showscale=True)
    return fig


def _upper_triangle_mask(corr: pd.DataFrame) -> pd.DataFrame:
    """Zero out the upper triangle of a correlation matrix (keep only lower + diagonal)."""
    mask = corr.values.copy()
    for i in range(len(mask)):
        for j in range(i + 1, len(mask)):
            mask[i][j] = None  # mask upper triangle (row < col), keep lower + diagonal
    return pd.DataFrame(mask, index=corr.index, columns=corr.columns)


def _empty_figure(message: str) -> go.Figure:
    """Return a figure displaying a single message."""
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font_size=16)
    fig.update_layout(xaxis_visible=False, yaxis_visible=False)
    return fig
