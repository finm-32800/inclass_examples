"""Path settings using chartbook.env.

This module uses chartbook's get_project_root() to find the project root
by searching upward for marker files like .git, pyproject.toml, or .env.

No custom path logic needed - chartbook handles it all.
"""

import chartbook.env

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"


def config(var_name: str):
    """Retrieve a configuration variable by name."""
    return globals()[var_name]


if __name__ == "__main__":
    print(f"BASE_DIR:   {BASE_DIR}")
    print(f"DATA_DIR:   {DATA_DIR}")
    print(f"OUTPUT_DIR: {OUTPUT_DIR}")
