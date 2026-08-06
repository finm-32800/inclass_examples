"""Minimal doit pipeline: pull latest prices, then build the HTML page.

Deliberately bare-bones (no custom reporter, no settings module) as a contrast
with ../01_fred_chartbook/. Run with:
    doit
"""

DOIT_CONFIG = {
    "backend": "sqlite3",
    "dep_file": "./.doit-db.sqlite",
}


def task_pull():
    """Pull latest Treasury futures prices from Databento"""
    return {
        "actions": ["python 01_pull_prices.py"],
        "targets": ["_output/latest_prices.parquet"],
        "file_dep": ["01_pull_prices.py"],
        # Fresh prices are the point: never consider this task up to date.
        "uptodate": [False],
    }


def task_page():
    """Build the standalone HTML price chart"""
    return {
        "actions": ["python 02_make_page.py"],
        "targets": ["_output/index.html"],
        "file_dep": ["02_make_page.py", "_output/latest_prices.parquet"],
        "clean": True,
    }
