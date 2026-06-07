"""Application-wide constants — single source of truth for config values."""

# Streamlit server defaults
DEFAULT_PORT = 8004
DEFAULT_HOST = "0.0.0.0"

# Model thresholds
AUC_MIN = 0.75
ACCURACY_MIN = 0.80

# Data
EXPECTED_FEATURES = [
    "age",
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
]
TARGET_COLUMN = "y"
