"""PyDoit task definitions for the package_approach demo.

Run with:
    doit              # Run all tasks
    doit list         # List available tasks
    doit demo_script  # Run specific task
    uv run doit       # Run with uv

This dodo.py demonstrates that the package approach works in task runners too.
"""

from pathlib import Path

# Get paths from our installed package - this is the key demonstration!
# The same imports work in dodo.py as they do in scripts and notebooks.
from myproj import project_root, data_dir, output_dir


def task_setup():
    """Ensure _data and _output directories exist."""

    def create_dirs():
        data_dir().mkdir(exist_ok=True)
        output_dir().mkdir(exist_ok=True)
        print(f"Created: {data_dir()}")
        print(f"Created: {output_dir()}")

    return {
        "actions": [create_dirs],
        "verbosity": 2,
    }


def task_demo_script():
    """Run the demo script to show paths working."""
    script = project_root() / "src" / "demo_script.py"
    return {
        "actions": [f"python {script}"],
        "file_dep": [script],
        "task_dep": ["setup"],
        "verbosity": 2,
    }


def task_demo_notebook():
    """Execute the demo notebook and convert to HTML."""
    notebook = project_root() / "src" / "demo_notebook.ipynb"
    output_html = output_dir() / "demo_notebook.html"

    return {
        "actions": [
            f"jupyter nbconvert --execute --to html --output {output_html} {notebook}",
        ],
        "file_dep": [notebook],
        "targets": [output_html],
        "task_dep": ["setup"],
        "verbosity": 2,
    }
