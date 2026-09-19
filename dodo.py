"""Master task runner for the in-class examples repo.

This intentionally wires up *only* the notebooks that the course textbook pulls
in at build time (see ``../finm32800_textbook/dodo.py``). Most examples in this repo are
standalone and are run directly from their own directories; as more material is
referenced by the textbook, add the corresponding entries to ``notebook_tasks``
below.

Notebooks are authored as jupytext percent-format ``.py`` files (the version
that gets committed). Each task converts the ``.py`` source to ``.ipynb``,
executes it, writes an HTML copy to ``_output/``, and moves the executed
notebook to ``_output/_notebook_build/``.

Tasks flagged ``keep_executed`` additionally leave the executed ``.ipynb``
next to its ``.py`` source so it can be committed. The textbook copies that
committed notebook directly instead of executing anything at book-build time
(see ``../finm32800_textbook/dodo.py``); refresh it by re-running the task here and
committing the result.

Paths are anchored to this file's location so the tasks behave the same whether
you run ``doit`` from this directory or the textbook invokes them with
``doit -f ../inclass_examples/dodo.py``.
"""

import shutil
from os import environ
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT_DIR = HERE / "_output"
NOTEBOOK_BUILD_DIR = OUTPUT_DIR / "_notebook_build"

environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"


# fmt: off
## Helper functions for automatic execution of Jupyter notebooks
def jupyter_execute_notebook(notebook_path):
    return f'jupyter nbconvert --execute --to notebook --ClearMetadataPreprocessor.enabled=True --ExecutePreprocessor.timeout=600 --inplace "{notebook_path}"'
def jupyter_to_html(notebook_path, output_dir=OUTPUT_DIR):
    return f'jupyter nbconvert --to html --output-dir="{output_dir}" "{notebook_path}"'
# fmt: on


def mv(from_path, to_path):
    """Move a file into a folder, creating the folder if needed (portable)."""

    def _mv():
        to_path.mkdir(parents=True, exist_ok=True)
        shutil.move(str(from_path), str(to_path / from_path.name))

    return _mv


def cp(from_path, to_path):
    """Copy a file into a folder, creating the folder if needed (portable)."""

    def _cp():
        to_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(from_path), str(to_path / from_path.name))

    return _cp


# Notebooks pulled by the textbook build. Keys are the notebook stems; each
# ``path`` points at the jupytext percent-format .py source. ``file_dep`` lists
# anything besides the source that should trigger a re-run.
notebook_tasks = {
    "01_wrds_python_package_ipynb": {
        "path": HERE / "wrds" / "01_wrds_python_package_ipynb.py",
        "file_dep": [HERE / "wrds" / "settings.py"],
        "targets": [],
    },
    "01_databento_ipynb": {
        "path": HERE / "databento" / "01_databento_ipynb.py",
        "file_dep": [HERE / "databento" / "settings.py"],
        "targets": [],
        # The executed notebook is committed and copied by the textbook build
        # (which never executes it); see the module docstring.
        "keep_executed": True,
    },
}


def task_run_notebooks():
    """Convert jupytext .py sources to notebooks, execute, and publish.

    Executing the WRDS notebook requires the ``wrds`` package and WRDS
    credentials (``WRDS_USERNAME`` in the repo-root ``.env`` plus a
    ``~/.pgpass`` entry).
    """
    for notebook, spec in notebook_tasks.items():
        pyfile_path = spec["path"]
        notebook_path = pyfile_path.with_suffix(".ipynb")
        keep_executed = spec.get("keep_executed", False)
        publish = cp if keep_executed else mv
        yield {
            "name": notebook,
            "actions": [
                f'jupytext --to notebook --output "{notebook_path}" "{pyfile_path}"',
                jupyter_execute_notebook(notebook_path),
                jupyter_to_html(notebook_path),
                publish(notebook_path, NOTEBOOK_BUILD_DIR),
            ],
            "file_dep": [pyfile_path, *spec["file_dep"]],
            "targets": [
                OUTPUT_DIR / f"{notebook}.html",
                NOTEBOOK_BUILD_DIR / f"{notebook}.ipynb",
                *([notebook_path] if keep_executed else []),
                *spec["targets"],
            ],
            "clean": True,
            "verbosity": 2,  # stream output in case WRDS prompts for credentials
        }
