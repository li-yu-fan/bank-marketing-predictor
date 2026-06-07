"""Tests for predictor module."""

import numpy as np
import pandas as pd

from src.config import EXPECTED_FEATURES, TARGET_COLUMN
from src.model_trainer import (
    evaluate_models,
    get_best_model,
    preprocess_data,
    save_model,
    train_models,
)
from src.predictor import load_model, predict, validate_input


def _make_synthetic_df(n: int = 200) -> pd.DataFrame:
    """Same synthetic dataset builder as used in model_trainer tests."""
    rng = np.random.RandomState(42)
    n_half = n // 2
    df = pd.DataFrame()
    for i, col in enumerate(EXPECTED_FEATURES):
        if i < 10:
            df[col] = np.concatenate([rng.randn(n_half), rng.randn(n_half) + 2.0])
        else:
            vals0 = rng.choice(["A", "B"], n_half)
            vals1 = rng.choice(["C", "D"], n_half)
            df[col] = np.concatenate([vals0, vals1])
    df[TARGET_COLUMN] = ["no"] * n_half + ["yes"] * n_half
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


def _train_and_save(tmp_path) -> tuple[dict, dict]:
    """Helper: train a model on synthetic data, save to tmp_path, return bundle + one valid input."""
    df = _make_synthetic_df()
    data = preprocess_data(df)
    models = train_models(data["X_train"], data["y_train"])
    metrics = evaluate_models(models, data["X_test"], data["y_test"])
    _, best = get_best_model(models, metrics)
    path = str(tmp_path / "test_model.pkl")
    save_model(best, data["preprocessor"], path)
    # Return one valid user input row (raw values from the original DataFrame)
    sample = df.iloc[0].to_dict()
    # Remove target, keep only feature values
    sample = {k: v for k, v in sample.items() if k in EXPECTED_FEATURES}
    return load_model(path), sample


class TestLoadModel:
    def test_loads_bundle_with_model_and_preprocessor(self, tmp_path):
        bundle, _ = _train_and_save(tmp_path)
        assert "model" in bundle
        assert "preprocessor" in bundle


class TestValidateInput:
    def test_empty_errors_for_valid_input(self):
        sample = {col: "test" for col in EXPECTED_FEATURES}
        assert validate_input(sample) == []

    def test_reports_missing_field(self):
        sample = {col: "test" for col in EXPECTED_FEATURES if col != "age"}
        errors = validate_input(sample)
        assert any("age" in e for e in errors)

    def test_reports_empty_string(self):
        sample = {col: "test" for col in EXPECTED_FEATURES}
        sample["age"] = ""
        errors = validate_input(sample)
        assert any("age" in e for e in errors)

    def test_reports_none_value(self):
        sample = {col: "test" for col in EXPECTED_FEATURES}
        sample["age"] = None
        errors = validate_input(sample)
        assert any("age" in e for e in errors)


class TestPredict:
    def test_returns_yes_or_no_for_valid_input(self, tmp_path):
        bundle, sample = _train_and_save(tmp_path)
        result = predict(bundle, sample)
        assert result["error"] is None
        assert result["prediction"] in ("yes", "no")
        assert 0 <= result["probability"] <= 1

    def test_returns_error_for_invalid_input(self, tmp_path):
        bundle, _ = _train_and_save(tmp_path)
        result = predict(bundle, {"age": 30})  # missing 19 features
        assert result["error"] is not None
        assert result["prediction"] is None
        assert result["probability"] is None

    def test_handles_edge_case_values(self, tmp_path):
        """Prediction should not crash on extreme numeric values."""
        bundle, sample = _train_and_save(tmp_path)
        for col in EXPECTED_FEATURES[:10]:  # numeric columns
            sample[col] = -9999
        result = predict(bundle, sample)
        # Should not crash — may or may not error depending on model
        assert isinstance(result, dict)
        assert "prediction" in result
