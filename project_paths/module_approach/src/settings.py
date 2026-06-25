"""Path settings anchored on settings.py location.

This module provides paths relative to the project root.
The key insight: settings.py's __file__ provides a stable anchor point.

Unlike the package approach, this doesn't require pip install -e .
Instead, callers add src/ to sys.path before importing.
"""

from pathlib import Path

# Auto-detect project root (settings.py -> src/ -> project_root/)
BASE_DIR = Path(__file__).resolve().parents[1]

# Project directories as absolute paths
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"


def config(var_name: str):
    """Retrieve a configuration variable by name.

    Args:
        var_name: Name of the variable (e.g., "DATA_DIR", "OUTPUT_DIR")

    Returns:
        The value of the configuration variable.
    """
    return globals()[var_name]


if __name__ == "__main__":
    print(f"BASE_DIR:   {BASE_DIR}")
    print(f"DATA_DIR:   {DATA_DIR}")
    print(f"OUTPUT_DIR: {OUTPUT_DIR}")
