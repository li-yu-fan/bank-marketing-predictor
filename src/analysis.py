"""Statistical analysis functions for Bank Marketing dataset."""

import pandas as pd

from src.config import TARGET_COLUMN


def get_numeric_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics (count, mean, std, min, 25%, 50%, 75%, max)
    for all numeric columns in the DataFrame."""
    return df.describe()


def get_target_distribution(df: pd.DataFrame) -> dict:
    """Return counts and proportions for each class in the target column."""
    if TARGET_COLUMN not in df.columns:
        return {}
    counts = df[TARGET_COLUMN].value_counts().to_dict()
    total = len(df)
    proportions = (
        {k: round(v / total, 4) for k, v in counts.items()} if total > 0 else {}
    )
    return {"counts": counts, "proportions": proportions, "total": total}


def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return Pearson correlation matrix for all numeric columns."""
    return df.corr(numeric_only=True)


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of columns with missing values: column name, count, percentage."""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        return pd.DataFrame(columns=["column", "missing_count", "missing_pct"])
    result = pd.DataFrame(
        {
            "column": missing.index,
            "missing_count": missing.values,
            "missing_pct": (missing.values / len(df) * 100).round(2),
        }
    ).reset_index(drop=True)
    return result
