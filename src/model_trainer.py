"""Model training and evaluation for Bank Marketing subscription prediction."""

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import AUC_MIN, EXPECTED_FEATURES, TARGET_COLUMN


def _separate_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split DataFrame into feature matrix X and target vector y."""
    X = (
        df[EXPECTED_FEATURES].copy()
        if EXPECTED_FEATURES
        else df.drop(columns=[TARGET_COLUMN])
    )
    y = df[TARGET_COLUMN].map({"yes": 1, "no": 0})
    return X, y


def _build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Build a ColumnTransformer: StandardScaler for numeric, OneHotEncoder for categorical."""
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    return ColumnTransformer(
        [
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(drop="first", sparse_output=False), categorical_cols),
        ],
        remainder="drop",
    )


def preprocess_data(
    df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> dict:
    """Split data, fit preprocessor, return train/test sets + fitted preprocessor.

    Returns a dict with keys: X_train, X_test, y_train, y_test, preprocessor.
    """
    X, y = _separate_xy(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    preprocessor = _build_preprocessor(X)
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "preprocessor": preprocessor,
    }


def train_models(X_train, y_train, random_state: int = 42) -> dict:
    """Train Logistic Regression and Random Forest. Return dict of fitted models."""
    lr = LogisticRegression(max_iter=2000, random_state=random_state)
    rf = RandomForestClassifier(n_estimators=100, random_state=random_state)
    lr.fit(X_train, y_train)
    rf.fit(X_train, y_train)
    return {"LogisticRegression": lr, "RandomForest": rf}


def evaluate_models(models: dict, X_test, y_test) -> pd.DataFrame:
    """Return a DataFrame with AUC, Accuracy, F1 for each model."""
    rows = []
    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_proba = (
            model.predict_proba(X_test)[:, 1]
            if hasattr(model, "predict_proba")
            else None
        )
        row = {
            "model": name,
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "f1": round(f1_score(y_test, y_pred), 4),
            "auc": round(roc_auc_score(y_test, y_proba), 4)
            if y_proba is not None
            else None,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def get_best_model(models: dict, metrics: pd.DataFrame) -> tuple[str, object]:
    """Return (model_name, model) with the highest AUC. Break ties by F1."""
    best_row = metrics.sort_values(["auc", "f1"], ascending=False).iloc[0]
    best_name = best_row["model"]
    return best_name, models[best_name]


def meets_threshold(metrics: pd.DataFrame) -> bool:
    """Check whether the best model meets minimum AUC threshold."""
    best_auc = metrics["auc"].max()
    return best_auc >= AUC_MIN


def save_model(model, preprocessor, path: str) -> None:
    """Persist model and preprocessor as a bundle dict to disk."""
    import os

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    joblib.dump({"model": model, "preprocessor": preprocessor}, path)
