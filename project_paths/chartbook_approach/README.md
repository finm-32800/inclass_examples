# Chartbook Approach for Project Paths

This example demonstrates using the **chartbook.env** module for project-root-anchored paths.

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

Use `chartbook.env.get_project_root()` which finds the project root by searching upward for marker files like `.git`, `pyproject.toml`, or `.env`.

```python
# In any script in src/, import settings directly
from settings import config

DATA_DIR = config("DATA_DIR")
OUTPUT_DIR = config("OUTPUT_DIR")

df = pd.read_csv(DATA_DIR / "raw" / "prices.csv")
fig.savefig(OUTPUT_DIR / "charts" / "analysis.png")
```

## Setup

Install the required package:

```bash
cd chartbook_approach
pip install -r requirements.txt
```

Then run from the project root:

```bash
python src/demo_script.py
```

Or use doit:

```bash
doit
```

## How It Works

The magic is in [src/settings.py](src/settings.py):

```python
import chartbook.env

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"
OUTPUT_DIR = BASE_DIR / "_output"
```

`chartbook.env.get_project_root()` searches upward from the current file until it finds a marker file:
- `.git`
- `pyproject.toml`
- `.env`
- `.env.example`
- `requirements.txt`

This is more robust than hardcoding parent levels because it adapts to your project structure.

## Project Structure

```
chartbook_approach/
├── requirements.txt         # chartbook>=0.0.3
├── dodo.py                  # Task runner (uses sys.path trick)
├── src/
│   ├── settings.py          # Uses chartbook.env.get_project_root()
│   └── demo_script.py       # Demo script
├── _data/                   # Data directory
└── _output/                 # Output directory
```

## Why This Approach?

| Pros | Cons |
|------|------|
| No hardcoded parent levels | Requires `pip install chartbook` |
| Adapts to project structure | Must run from project root |
| Uses standard marker files | |
| Simple settings.py | |

## Comparison with Module Approach

| Aspect | Module Approach | Chartbook Approach |
|--------|-----------------|-------------------|
| Path detection | `Path(__file__).parents[1]` | Marker file search |
| Dependencies | None | chartbook package |
| Flexibility | Fixed structure | Adapts to markers |
| Robustness | Breaks if structure changes | More resilient |

## See Also

- [chartbook.env documentation](https://backofficedev.github.io/chartbook/apidocs/chartbook/chartbook.env.html)
