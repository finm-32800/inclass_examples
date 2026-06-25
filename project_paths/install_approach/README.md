# Install Approach for Project Paths

This example demonstrates the **editable install** approach for project-root-anchored paths.

## The Problem

In data science projects, you often have:
- Scripts in `src/`
- Notebooks in `src/` or `notebooks/`
- Data in `_data/`
- Outputs in `_output/`

You want paths that work the same way regardless of:
- Which file you're running from
- What your current working directory is
- Whether you're in a script or notebook

## The Solution

Install your project as an editable package. Then `myproj.__file__` provides a stable anchor point.

```python
# This works everywhere: scripts, notebooks, dodo.py, tests
from myproj import data_path, output_path

df = pd.read_csv(data_path("raw", "prices.csv"))
fig.savefig(output_path("charts", "analysis.png"))
```

## Setup

### With uv (recommended)

```bash
cd install_approach
uv venv
uv pip install -e .
```

### With pip

```bash
cd install_approach
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

## Usage

### Run all tasks

```bash
doit
# or
uv run doit
```

### Run individual tasks

```bash
doit demo_script    # Run the demo script
doit demo_notebook  # Execute and convert the notebook
doit list           # List all available tasks
```

### Use in your code

```python
from myproj import project_root, data_path, output_path

# Get project root
print(project_root())  # /path/to/install_approach

# Build data paths
data_path()                       # /path/to/install_approach/_data
data_path("raw")                  # /path/to/install_approach/_data/raw
data_path("raw", "prices.csv")    # /path/to/install_approach/_data/raw/prices.csv

# Build output paths
output_path("charts", "fig.png")  # /path/to/install_approach/_output/charts/fig.png
```

## How It Works

The magic is in [src/myproj/paths.py](src/myproj/paths.py):

```python
from pathlib import Path

def project_root() -> Path:
    # paths.py -> myproj/ -> src/ -> project_root/
    # That's 3 levels up, so parents[2] (0-indexed)
    return Path(__file__).resolve().parents[2]
```

When you install with `pip install -e .`:
1. Python can find `myproj` from anywhere
2. `__file__` in `paths.py` always points to the actual source file
3. We calculate project root relative to that file

## Notebook Kernel Setup

For notebooks to work, the kernel must use the project's virtual environment:

1. Install ipykernel: `pip install ipykernel`
2. Register the kernel: `python -m ipykernel install --user --name myproj`
3. Select "myproj" kernel in your notebook

Or simply run notebooks from within the activated virtual environment.

## Project Structure

```
install_approach/
├── pyproject.toml           # Package configuration
├── dodo.py                  # Task runner (uses myproj imports!)
├── src/
│   ├── myproj/              # The installable package
│   │   ├── __init__.py      # Exposes path functions
│   │   └── paths.py         # Core path utilities
│   ├── demo_script.py       # Demo script
│   └── demo_notebook.ipynb  # Demo notebook
├── _data/                   # Data directory (gitignored)
└── _output/                 # Output directory (gitignored)
```

## Why This Approach?

| Pros | Cons |
|------|------|
| Clean, explicit imports | Requires `pip install -e .` |
| Works everywhere (scripts, notebooks, tests, dodo.py) | Need to understand virtual environments |
| No environment variables to manage | |
| No marker-walk overhead | |
| IDE autocomplete works | |
