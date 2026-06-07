"""Tests for the Streamlit app entry point."""


def test_app_parses_without_syntax_error():
    """app.py should parse cleanly as valid Python."""
    with open("app.py", encoding="utf-8") as f:
        source = f.read()
    compile(source, "app.py", "exec")
