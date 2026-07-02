# WRDS

In-class examples for pulling data from [WRDS](https://wrds-www.wharton.upenn.edu/)
(Wharton Research Data Services) with the [`wrds`](https://pypi.org/project/wrds/)
Python package.

## Contents

| File | Description |
|------|-------------|
| [`01_wrds_python_package_ipynb.py`](01_wrds_python_package_ipynb.py) | Walkthrough of the `wrds` Python package: connecting, browsing libraries, and pulling CRSP data. |
| [`settings.py`](settings.py) | Minimal `config()` helper the notebook uses to read `WRDS_USERNAME` and output paths. |

## How this notebook is built

The notebook is authored as a jupytext percent-format `.py` file — that is the
version that gets committed and edited. The master [`dodo.py`](../dodo.py) at
the repo root converts it to `.ipynb`, executes it against WRDS, and publishes
the results to the repo-root `_output/` directory:

```bash
# from the repo root
doit
# executed notebook: _output/_notebook_build/01_wrds_python_package_ipynb.ipynb
# HTML copy:         _output/01_wrds_python_package_ipynb.html
```

The course textbook build pulls the executed notebook from
`_output/_notebook_build/`, so this task must be able to run against WRDS.
That requires WRDS credentials: `WRDS_USERNAME` in the repo-root `.env` plus a
`~/.pgpass` entry (see
[`../env_vars/05_wrds_credentials/`](../env_vars/05_wrds_credentials/)).

To work on the notebook interactively, open the `.py` file directly in
Jupyter (via the jupytext extension) or convert it yourself:

```bash
jupytext --to notebook 01_wrds_python_package_ipynb.py
```
