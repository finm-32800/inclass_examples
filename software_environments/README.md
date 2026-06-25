# Software Environments

Four ways to manage a Python project's dependencies and isolated
environment — **each running the exact same script**. The code
([`analyze.py`](01_conda_only/analyze.py)) and its dependencies
(`numpy`, `pandas`, `matplotlib`) are identical in every subdirectory;
only the *tooling* around installation and running changes.

This pairs with the Week 1 "Virtual Environments" chapter in the textbook.

## The Shared App

A tiny, dependency-bearing finance demo so the environment tool actually
matters: it simulates a reproducible random-walk price series, computes
20- and 50-day moving averages, reports the most recent golden/death
cross, and saves a chart to `prices.png`. No network or API keys needed.

## Examples

| Directory | Tool | Manifest | One-liner |
|-----------|------|----------|-----------|
| [01_conda_only](01_conda_only/) | conda alone | `environment.yml` | Everything (incl. Python) from conda-forge |
| [02_conda_and_pip](02_conda_and_pip/) | conda + pip | `environment.yml` + `requirements.txt` | Conda for Python, pip for packages (textbook's pick) |
| [03_uv](03_uv/) | uv | `pyproject.toml` | One fast Rust tool; `uv run analyze.py` does it all |
| [04_pixi](04_pixi/) | pixi | `pixi.toml` | uv-style workflow over conda channels |

## How They Compare

| | conda only | conda + pip | uv | pixi |
|---|---|---|---|---|
| Package source | conda channels | conda (Python) + PyPI | PyPI | conda channels (+ PyPI) |
| Manages Python version | ✅ | ✅ | ✅ | ✅ |
| Non-Python binaries | ✅ | ✅ (via conda) | ❌ | ✅ |
| Lockfile | manual | manual | `uv.lock` (auto) | `pixi.lock` (auto) |
| Speed | slower | faster installs | very fast | very fast |
| Run command | `python analyze.py` | `python analyze.py` | `uv run analyze.py` | `pixi run start` |

## Quick Start (pick one)

```bash
# conda only
cd 01_conda_only && conda env create -f environment.yml && conda activate finm-env-conda && python analyze.py

# conda + pip
cd 02_conda_and_pip && conda env create -f environment.yml && conda activate finm-env-conda-pip && pip install -r requirements.txt && python analyze.py

# uv
cd 03_uv && uv run analyze.py

# pixi
cd 04_pixi && pixi run start
```

## See Also: End-Product Motivation

These examples focus on the *mechanics* of four environment tools. For
motivation — what reproducible environments let you **build and share** —
see the Streamlit finance dashboards in the Week 1 "Virtual Environments"
chapter of the textbook:

- [`streamlit_finance_chart`](https://github.com/jmbejara/streamlit_finance_chart) —
  S&P 500 price charts with moving averages (installed via conda + pip)
- [`FinStockDash`](https://github.com/jmbejara/FinStockDash) — a
  financial-ratios dashboard (installed via `venv` + pip; needs API keys)

Those are full web apps you reproduce from a shared environment file; the
examples here strip that down to isolate the tooling differences.

## The Takeaway

Same code, four toolchains. conda is the long-standing data-science
default (and the only one here that natively handles non-Python binaries
on its own channels); conda+pip is the pragmatic hybrid the textbook
recommends; **uv** and **pixi** are the fast, modern, lockfile-first tools
— uv from the PyPI world, pixi from the conda world.
