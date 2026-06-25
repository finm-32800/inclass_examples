"""Master task runner for the in-class examples repo.

This intentionally wires up *only* the examples that the course textbook pulls
in at build time. Right now that is the WRDS Python package notebook, which the
textbook copies into its build. As more material is migrated into this repo and
referenced by the textbook, add the corresponding tasks here.

Paths are anchored to this file's location so the tasks behave the same whether
you run ``doit`` from this directory or the textbook invokes them with
``doit -f ../inclass_examples/dodo.py``.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
WRDS_NOTEBOOK = HERE / "wrds" / "01_wrds_python_package_ipynb.ipynb"


def task_wrds_python_package():
    """Execute the WRDS Python package notebook in place.

    The textbook copies this notebook into its build, so we keep it executed
    (with outputs) here. Requires the ``wrds`` package and WRDS credentials
    (``WRDS_USERNAME`` in ``.env`` plus a ``~/.pgpass`` entry). nbconvert only
    overwrites the notebook on a successful run, so if WRDS can't be reached the
    committed copy is left intact and can still serve as the textbook's fallback.
    """
    return {
        "actions": [
            "jupyter nbconvert --execute --to notebook --inplace "
            "--ExecutePreprocessor.timeout=600 "
            f'"{WRDS_NOTEBOOK}"'
        ],
        "targets": [WRDS_NOTEBOOK],
        "uptodate": [False],  # always attempt a fresh pull when invoked
        "verbosity": 2,  # stream output in case WRDS prompts for credentials
    }
