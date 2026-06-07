"""Online prediction: load a trained model bundle and produce subscription predictions."""

import joblib
import pandas as pd

from src.config import EXPECTED_FEATURES

# Mapping from numeric prediction back to label
_LABEL_MAP = {1: "yes", 0: "no"}


def load_model(path: str) -> dict:
    """Load a saved model bundle (model + preprocessor) from disk."""
    return joblib.load(path)


def validate_input(user_input: dict) -> list[str]:
    """Return a list of validation error messages. Empty list means valid."""
    errors = []
    for col in EXPECTED_FEATURES:
        if col not in user_input:
            errors.append(f"缺少必填字段: {col}")
            continue
        val = user_input[col]
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"'{col}' 不能为空")
    return errors


def predict(bundle: dict, user_input: dict) -> dict:
    """Run prediction on a single sample.

    Args:
        bundle: {"model": ..., "preprocessor": ...} from load_model or model_trainer.
        user_input: dict with keys matching EXPECTED_FEATURES.

    Returns:
        {"prediction": "yes"/"no", "probability": 0.XX, "error": None}
        — or — {"prediction": None, "probability": None, "error": "message"}
    """
    errors = validate_input(user_input)
    if errors:
        return {"prediction": None, "probability": None, "error": "; ".join(errors)}

    model = bundle["model"]
    preprocessor = bundle["preprocessor"]

    # Build a single-row DataFrame in the correct feature order
    X_raw = pd.DataFrame([{col: user_input[col] for col in EXPECTED_FEATURES}])
    X_tf = preprocessor.transform(X_raw)

    proba = model.predict_proba(X_tf)[0]
    # Class order: 0 = no, 1 = yes (alphabetical by pd.get_dummies convention)
    # scikit-learn LabelEncoder also maps alphabetically: "no" < "yes" → 0, 1
    pred_idx = model.predict(X_tf)[0]
    prob_yes = (
        proba[1] if len(proba) > 1 else proba[0] if pred_idx == 1 else 1 - proba[0]
    )

    return {
        "prediction": _LABEL_MAP.get(int(pred_idx), "unknown"),
        "probability": round(float(prob_yes), 4),
        "error": None,
    }
