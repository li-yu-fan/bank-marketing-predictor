"""Tests for model_trainer module."""

import os

import numpy as np
import pandas as pd

from src.config import EXPECTED_FEATURES, TARGET_COLUMN
from src.model_trainer import (
    evaluate_models,
    get_best_model,
    meets_threshold,
    preprocess_data,
    save_model,
    train_models,
)


def _make_synthetic_df(n: int = 200) -> pd.DataFrame:
    """Synthetic dataset with 20 features + binary target, designed to be separable."""
    rng = np.random.RandomState(42)
    n_half = n // 2
    # Class 0: low values, class 1: high values — create signal for models to learn
    df = pd.DataFrame()
    for i, col in enumerate(EXPECTED_FEATURES):
        if i < 10:
            # Numeric features: class 0 ~ N(0,1), class 1 ~ N(2,1)
            df[col] = np.concatenate([rng.randn(n_half), rng.randn(n_half) + 2.0])
        else:
            # Categorical features: class 0 from [A,B], class 1 from [C,D]
            vals0 = rng.choice(["A", "B"], n_half)
            vals1 = rng.choice(["C", "D"], n_half)
            df[col] = np.concatenate([vals0, vals1])
    df[TARGET_COLUMN] = ["no"] * n_half + ["yes"] * n_half
    return df.sample(frac=1, random_state=42).reset_index(drop=True)


class TestPreprocessData:
    def test_returns_expected_keys(self):
        df = _make_synthetic_df()
        result = preprocess_data(df)
        for key in ["X_train", "X_test", "y_train", "y_test", "preprocessor"]:
            assert key in result

    def test_train_test_split_sizes(self):
        df = _make_synthetic_df(200)
        result = preprocess_data(df, test_size=0.2)
        assert len(result["y_train"]) == 160
        assert len(result["y_test"]) == 40

    def test_y_is_binary(self):
        df = _make_synthetic_df()
        result = preprocess_data(df)
        assert set(result["y_train"].unique()).issubset({0, 1})


class TestTrainModels:
    def test_returns_two_models(self):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        assert "LogisticRegression" in models
        assert "RandomForest" in models

    def test_models_have_predict(self):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        for model in models.values():
            preds = model.predict(data["X_test"])
            assert len(preds) == len(data["y_test"])


class TestEvaluateModels:
    def test_returns_dataframe_with_metrics(self):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        assert "model" in metrics.columns
        assert "auc" in metrics.columns
        assert "accuracy" in metrics.columns
        assert "f1" in metrics.columns
        assert len(metrics) == 2

    def test_auc_is_between_0_and_1(self):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        assert all(0 <= auc <= 1 for auc in metrics["auc"])


class TestGetBestModel:
    def test_returns_model_with_highest_auc(self):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        name, model = get_best_model(models, metrics)
        best_auc = metrics.loc[metrics["model"] == name, "auc"].values[0]
        assert best_auc == metrics["auc"].max()


class TestMeetsThreshold:
    def test_synthetic_data_exceeds_threshold(self):
        """Synthetic data is designed with strong signal — should pass AUC threshold."""
        df = _make_synthetic_df(200)
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        assert meets_threshold(metrics)

    def test_random_data_fails_threshold(self):
        """Pure noise should produce AUC near 0.5, below threshold."""
        rng = np.random.RandomState(42)
        df = pd.DataFrame()
        for col in EXPECTED_FEATURES:
            df[col] = rng.randn(100)
        df[TARGET_COLUMN] = rng.choice(["yes", "no"], 100)
        data = preprocess_data(df, test_size=0.3)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        # Pure random data — models should not learn, AUC ≈ 0.5
        assert not meets_threshold(metrics)


class TestSaveModel:
    def test_saves_and_file_exists(self, tmp_path):
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        _, best = get_best_model(models, metrics)
        path = str(tmp_path / "test_model.pkl")
        save_model(best, data["preprocessor"], path)
        assert os.path.isfile(path)

    def test_creates_parent_directories(self):
        """save_model should create intermediate directories automatically."""
        df = _make_synthetic_df()
        data = preprocess_data(df)
        models = train_models(data["X_train"], data["y_train"])
        metrics = evaluate_models(models, data["X_test"], data["y_test"])
        _, best = get_best_model(models, metrics)
        import tempfile

        path = os.path.join(tempfile.mkdtemp(), "subdir", "model.pkl")
        save_model(best, data["preprocessor"], path)
        assert os.path.isfile(path)
