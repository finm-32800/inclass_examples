# 01 Conda Only

Install **everything** — the Python interpreter and every package — from a
conda channel (`conda-forge`). No `pip` involved. This is the most
"classic" conda workflow.

## What You Learn

- How an `environment.yml` file fully describes an environment: name,
  channels, Python version, and packages
- That conda manages the Python interpreter itself, not just packages
- The create / activate / run loop

## Setup

```bash
conda env create -f environment.yml
conda activate finm-env-conda
```

## Run

```bash
python analyze.py
```

This prints a summary table and the most recent moving-average crossover,
and writes a chart to `prices.png`.

## Clean Up

```bash
conda deactivate
conda env remove --name finm-env-conda
```

## Key Concepts

| Piece | Role |
|-------|------|
| `name:` | The environment's name (used by `conda activate`) |
| `channels:` | Where conda looks for packages (`conda-forge` here) |
| `dependencies:` | Python version + packages, all from conda |

## Trade-offs

- **Pro:** One tool, one file. Can install non-Python binaries (e.g. C
  libraries, R, CUDA) that pip cannot.
- **Con:** Dependency resolution can be slow. Not every PyPI package is
  packaged for conda.

## Try It

- Add `scipy` to `environment.yml`, then run `conda env update -f environment.yml`
- Compare to `02_conda_and_pip/`, where conda supplies only Python and pip
  installs the rest — notice how much shorter the conda file becomes
