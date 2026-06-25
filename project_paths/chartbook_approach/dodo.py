"""PyDoit task definitions for the chartbook_approach demo.

Run with:
    doit              # Run all tasks
    doit list         # List available tasks
    doit demo_script  # Run specific task

This dodo.py demonstrates using chartbook.env for path configuration.
"""

import sys

# Add src/ to sys.path so we can import settings
sys.path.insert(0, "./src/")

from settings import config

BASE_DIR = config("BASE_DIR")
DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")


def task_setup():
    """Ensure _data and _output directories exist."""

    def create_dirs():
        DATA_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
        print(f"Created: {DATA_DIR}")
        print(f"Created: {OUTPUT_DIR}")

    return {
        "actions": [create_dirs],
        "verbosity": 2,
    }


def task_demo_script():
    """Run the demo script to show paths working."""
    script = BASE_DIR / "src" / "demo_script.py"
    return {
        "actions": [f"python {script}"],
        "file_dep": [script],
        "task_dep": ["setup"],
        "verbosity": 2,
    }
