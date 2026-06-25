# Module Approach for Project Paths

This example demonstrates the **simple module** approach for project-root-anchored paths.

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

Create a `settings.py` module that uses `__file__` to anchor paths to the project root.

```python
# In any script in src/, import settings directly
from settings import config

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")

df = pd.read_csv(DATA_DIR / "raw" / "prices.csv")
fig.savefig(OUTPUT_DIR / "charts" / "analysis.png")
```

## Setup

No installation required! Just run from the project root:

```bash
cd module_approach
python src/demo_script.py
```

Or use doit:

```bash
cd module_approach
doit
```

## Usage

### In scripts (within src/)

Scripts in `src/` can import settings directly:

```python
from settings import config

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")
```

### In dodo.py or external scripts

Add `src/` to `sys.path` before importing:

```python
import sys
sys.path.insert(0, "./src/")

from settings import config

DATA_DIR = config("DATA_DIR")
```

### In Jupyter notebooks

Add the path at the top of the notebook:

```python
import sys
sys.path.insert(0, "./src/")

from settings import config
DATA_DIR = config("DATA_DIR")
```

## How It Works

The magic is in [src/settings.py](src/settings.py):

```python
from pathlib import Path

# settings.py -> src/ -> project_root/
# That's 1 level up, so parents[1]
BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"


def config(var_name: str):
    return globals()[var_name]
```

Key insight: `__file__` in `settings.py` always points to the actual source file location, so we can calculate the project root relative to it.

## Project Structure

```
module_approach/
├── dodo.py                  # Task runner (uses sys.path trick)
├── src/
│   ├── settings.py          # Central path configuration
│   └── demo_script.py       # Demo script
├── _data/                   # Data directory
└── _output/                 # Output directory
```

## Why This Approach?

| Pros | Cons |
|------|------|
| No installation required | Must run from project root |
| No virtual environment needed | Requires `sys.path` modification in dodo.py |
| Simple, self-contained | Less robust than install approach |
| Easy to understand | Won't work from arbitrary directories |
| Good for quick projects | |

## Comparison with Install Approach

| Aspect | Module Approach | Install Approach |
|--------|-----------------|------------------|
| Setup | None | `pip install -e .` |
| Import | `from settings import config` | `from myproj import data_path` |
| Working directory | Must be project root | Works from anywhere |
| sys.path hack | Required in dodo.py | Not needed |
| Best for | Quick projects, teaching | Production, shared code |
