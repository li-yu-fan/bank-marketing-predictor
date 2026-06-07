"""Data loading and validation for Bank Marketing dataset."""

import os

import pandas as pd

from src.config import EXPECTED_FEATURES, TARGET_COLUMN


def load_csv(filepath: str) -> pd.DataFrame:
    """Read CSV file into a DataFrame.

    Raises FileNotFoundError if path doesn't exist; propagates pandas parse errors.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"数据文件不存在: {filepath}")
    return pd.read_csv(filepath)


def validate_columns(df: pd.DataFrame) -> list[str]:
    """Return a list of expected columns missing from the DataFrame."""
    required = EXPECTED_FEATURES + [TARGET_COLUMN]
    missing = [col for col in required if col not in df.columns]
    return missing


def get_data_summary(df: pd.DataFrame) -> dict:
    """Return a summary dict: row count, column count, missing values per column, dtypes."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": df.isnull().sum().to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }
