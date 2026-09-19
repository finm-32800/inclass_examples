# In-Class Examples

This directory contains small, self-contained examples used for in-class demonstrations in [FINM 32800: Data Pipelines for Quantitative Research](https://finm-32800.github.io/).

These examples are designed to illustrate specific concepts during lectures without requiring their own dedicated repositories.

## Contents

| Directory | Description |
|-----------|-------------|
| [databento/](databento/) | Databento market data: SDK vs raw API (HTTP and TCP) |
| [env_vars/](env_vars/) | Environment variables and configuration examples |
| [github_actions/](github_actions/) | Scheduled GitHub Actions: daily data pipelines, secrets, and gh-pages deployment |
| [latex/](latex/) | Progressive LaTeX examples from minimal to full articles and slides |
| [project_paths/](project_paths/) | Approaches for project-root-anchored paths |
| [polars/](polars/) | Polars vs pandas: syntax, LazyFrames, streaming, Hive partitioning |
| [pydoit/](pydoit/) | Progressive examples teaching PyDoit task automation |
| [software_environments/](software_environments/) | Same app, four ways: conda, conda+pip, uv, pixi |
| [sphinx/](sphinx/) | Sphinx documentation: quickstart, autodoc2, MyST, and themes |
| [wrds/](wrds/) | Pulling data from WRDS with the `wrds` Python package |

## How to Run

**Most examples are standalone.** Each subdirectory is self-contained: `cd`
into it and follow its README. They do not depend on the master `dodo.py`.

**A few notebooks are wired into the master [`dodo.py`](dodo.py)** because the
course textbook (`finm-32800/finm32800_textbook`) pulls their executed versions at build
time. Those notebooks are authored as jupytext percent-format `.py` files
(e.g. [`wrds/01_wrds_python_package_ipynb.py`](wrds/01_wrds_python_package_ipynb.py));
the committed `.py` file is the source of truth, and executed `.ipynb`/HTML
copies are build artifacts. To build them:

```bash
# from the repo root
doit
```

This converts each wired `.py` source to a notebook, executes it, and writes:

- `_output/_notebook_build/<name>.ipynb` — the executed notebook (what the textbook pulls)
- `_output/<name>.html` — an HTML copy for quick viewing

The WRDS notebook needs WRDS credentials to execute: copy `.env.example` to
`.env`, set `WRDS_USERNAME`, and set up `~/.pgpass` (see
[env_vars/05_wrds_credentials/](env_vars/05_wrds_credentials/)).

## Course Overview

FINM 32800 is a hands-on course centered on key data science tools in quantitative finance. It covers:

- **Data sources**: CRSP, Compustat, FRED, Bloomberg, and more
- **Development practices**: Git, virtual environments, task runners, testing
- **Analytics pipeline**: Data extraction, cleaning, analysis, visualization, reporting
- **Deployment**: GitHub Actions, interactive dashboards

See the [course website](https://finm-32800.github.io/) for more details.
