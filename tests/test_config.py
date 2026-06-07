"""Tests for config module."""

from src.config import (
    AUC_MIN,
    ACCURACY_MIN,
    DEFAULT_PORT,
    EXPECTED_FEATURES,
    TARGET_COLUMN,
)


def test_default_port_is_8004():
    assert DEFAULT_PORT == 8004


def test_auc_threshold_is_positive():
    assert 0 < AUC_MIN < 1.0


def test_accuracy_threshold_in_range():
    assert 0 < ACCURACY_MIN < 1.0


def test_target_column_is_subscribe():
    assert TARGET_COLUMN == "subscribe"


def test_expected_features_has_20_columns():
    # Bank Marketing dataset has exactly 20 input features
    assert len(EXPECTED_FEATURES) == 20


def test_expected_features_contains_key_columns():
    assert "age" in EXPECTED_FEATURES
    assert "job" in EXPECTED_FEATURES
    assert "duration" in EXPECTED_FEATURES
    assert "lending_rate3m" in EXPECTED_FEATURES
