# WRDS

In-class examples for pulling data from [WRDS](https://wrds-www.wharton.upenn.edu/)
(Wharton Research Data Services) with the [`wrds`](https://pypi.org/project/wrds/)
Python package.

## Contents

| File | Description |
|------|-------------|
| [`01_wrds_python_package_ipynb.ipynb`](01_wrds_python_package_ipynb.ipynb) | Walkthrough of the `wrds` Python package: connecting, browsing libraries, and pulling CRSP data. |

## A note on the committed outputs

`01_wrds_python_package_ipynb.ipynb` is committed **with its executed outputs**
on purpose. The course textbook build pulls this notebook in: it first tries to
rebuild a fresh copy from the `case_study_wrds_fama_french` repo (which runs the
notebook against WRDS), and if that repo can't be run, it falls back to the copy
committed here so the textbook can still compile. Re-running the notebook and
committing the result keeps that fallback current.

Running it yourself requires WRDS credentials in a `.env` file (see
[`../env_vars/05_wrds_credentials/`](../env_vars/05_wrds_credentials/)).
