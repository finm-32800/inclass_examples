# Project Paths

This directory demonstrates different approaches for handling **project-root-anchored paths** in Python data science projects.

## The Problem

When working on a data science project with files in multiple directories (`src/`, notebooks, scripts), you need paths that:

1. Work regardless of the current working directory
2. Work the same way in `.py` scripts and `.ipynb` notebooks
3. Always point to the same `_data/` and `_output/` directories

Relative paths like `Path("_data/file.csv")` break when you run code from different locations.

## Approaches

| Directory | Approach | Description | Dependencies |
|-----------|----------|-------------|--------------|
| [module_approach/](module_approach/) | Simple Module | Hardcode `Path(__file__).parents[N]` | None |
| [install_approach/](install_approach/) | Editable Install | Use `pip install -e .` | setuptools |
| [chartbook_approach/](chartbook_approach/) | chartbook.env | Marker file search (Recommended) | chartbook |

## 1. Module Approach (Simplest)

The simplest approach: create a `settings.py` that calculates paths relative to its own location.

```python
# src/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # Go up to project root
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
```

**Pros:** No dependencies, easy to understand
**Cons:** Hardcoded parent levels break if you reorganize; must run from project root

See [module_approach/](module_approach/) for the full example.

## 2. Install Approach (Most Flexible)

Install your project as an editable package with `pip install -e .`. Then the package location provides a stable anchor.

```python
# After: pip install -e .
from myproj import data_path, output_path

df = pd.read_csv(data_path("raw", "prices.csv"))
```

**Pros:** Works from any directory; clean imports; IDE autocomplete
**Cons:** Requires virtual environment setup and `pip install -e .`

See [install_approach/](install_approach/) for the full example.

## 3. Chartbook Approach (Recommended)

Use `chartbook.env.get_project_root()` which searches upward for marker files (`.git`, `pyproject.toml`, `.env`). This combines the simplicity of the module approach with more robust path detection.

```python
# src/settings.py
import chartbook.env

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
```

**Pros:** No hardcoded parent levels; adapts to project structure; simple setup
**Cons:** Requires `pip install chartbook`

See [chartbook_approach/](chartbook_approach/) for the full example.

## Quick Comparison

| Aspect | Module | Install | Chartbook |
|--------|--------|---------|-----------|
| Setup complexity | None | `pip install -e .` | `pip install chartbook` |
| Path detection | Hardcoded parents | Package location | Marker file search |
| Works from any directory | No | Yes | No (but more robust) |
| Dependencies | None | setuptools | chartbook |
| Recommended for | Learning | Production | Most projects |

## See Also

- [env_vars/](../env_vars/) - Examples of environment variable handling
- [pydoit/](../pydoit/) - Examples of PyDoit task automation
