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
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
TARGET_COLUMN = "subscribe"
