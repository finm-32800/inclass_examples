# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Modules, Packages, and `if __name__ == "__main__"`
#
# Every pipeline in this course is a folder of `.py` files that import one
# another. A guide notebook runs `import pull_fed_funds_futures` and calls
# `load_fed_funds_futures()`. `dodo.py` runs the same file as a script, with
# `python ./src/pull_fed_funds_futures.py`. And code that more than one
# repository needs, such as `finm` or `chartbook`, goes one step further: it
# becomes a package that each repository installs.
#
# This notebook walks through the small examples in the
# [`python_imports/`](https://github.com/finm-32800/inclass_examples/tree/main/python_imports)
# folder of the in-class examples repository, from a single file to an
# installable package. Then it explains the `if __name__ == "__main__":` block
# at the bottom of nearly every module in this course.
#
# Each example is a folder you can run yourself: `cd` into it and run
# `python main.py`. Here the notebook runs them and prints what they print.

# %%
import os
import subprocess
import sys
from pathlib import Path

HERE = Path.cwd()  # the python_imports/ folder, where this notebook runs


def show(path):
    """Print one of the example files, with its path as a header."""
    path = (HERE / path).resolve()
    print(f"--- {path.relative_to(HERE.parent)} ---")
    print(path.read_text().rstrip())


def run(script, folder):
    """Run `python <script>` inside `folder` and print its output.

    Paths in the output are shortened: `~` is your home folder and `<env>` is
    the folder of the Python environment the notebook runs in.
    """
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, script],
        cwd=HERE / folder,
        env=env,
        capture_output=True,
        text=True,
    )
    print(f"$ cd {folder} && python {script}")
    output = result.stdout + result.stderr
    output = output.replace(sys.prefix, "<env>").replace(str(Path.home()), "~")
    print(output.rstrip())


# %% [markdown]
# ## A module is a file
#
# Any `.py` file is a **module**. Another file in the same folder can import
# it by its name, without the `.py`:

# %%
show("01_simple_module/mypackage.py")
show("01_simple_module/main.py")
run("main.py", "01_simple_module")

# %% [markdown]
# This is how the files in a course repository's `src/` folder use one
# another. Every module there starts with `from settings import config`:
# `settings.py` is a module in the same folder.

# %% [markdown]
# ## A package is a folder
#
# A folder that contains an `__init__.py` file is a **package**. It is
# imported the same way as a module, and the code in `__init__.py` runs when
# it is. A package can hold many modules, which are then imported as
# `mypackage.something`.

# %%
show("02_package_directory/mypackage/__init__.py")
show("02_package_directory/main.py")
run("main.py", "02_package_directory")

# %% [markdown]
# ## Where Python looks
#
# `import mypackage` works because Python searches a list of folders,
# `sys.path`, in order, and the folder of the script you ran comes first.
# That is also how an import goes wrong. A file of your own named `numpy.py`
# hides the real NumPy:

# %%
show("03_name_shadowing/main.py")
run("main.py", "03_name_shadowing")

# %% [markdown]
# Two consequences for this course's repositories:
#
# - `python ./src/pull_fed_funds_futures.py` can `import settings`, because
#   `src/` is the script's own folder and so comes first on `sys.path`.
#   `dodo.py` lives one folder up, so it puts `src/` on the path itself: that
#   is the `sys.path.insert(1, "./src/")` line at its top.
# - Never name a file after a package you use: no `pandas.py`, `wrds.py`, or
#   `doit.py` in your project.

# %% [markdown]
# ## An installable package
#
# Code that more than one project needs should not be copied from one to the
# next. It becomes a package that each project installs. The smallest example
# is in
# [`project_paths/install_approach/`](https://github.com/finm-32800/inclass_examples/tree/main/project_paths/install_approach):
# a package, `src/myproj/`, and a `pyproject.toml` that says what it is called,
# where its code is, and what it depends on.

# %%
show("../project_paths/install_approach/pyproject.toml")

# %% [markdown]
# Each table in the file has one job. `[build-system]` names the tool that
# turns the source into an installable package, here Hatchling, and `pip`
# reads it to know how to build. `[project]` describes the package itself: its
# name, its version, the Python it needs, and the packages it depends on.
# `[tool.hatch.build.targets.wheel]` is a setting for Hatchling alone: it says
# the package's code is in `src/myproj`.
#
# `pip install -e .`, or `uv pip install -e .`, reads that file and puts
# `myproj` on `sys.path` for good, so `import myproj` works from any folder,
# in any script or notebook that uses the same environment. The `-e`, for
# *editable*, links to the source rather than copying it, so an edit to
# `src/myproj/paths.py` takes effect at the next import.
#
# `finm`, `chartbook`, `databento`, and `wrds` are packages of exactly this
# shape, published to PyPI so that `pip install` can fetch them by name.
# [Writing and Publishing Your Own Python Packages](https://finm-32800.github.io/Week6/python_packaging_with_hatch.html)
# takes it from here.

# %% [markdown]
# ## `if __name__ == "__main__"`
#
# Every module has a variable called `__name__`. When the module is imported,
# `__name__` is the module's name, `"greet"` for a file called `greet.py`. When
# the file is the one you run, as in `python greet.py`, Python sets `__name__`
# to `"__main__"` instead. So a block under `if __name__ == "__main__":` runs
# when the file is run as a script, and is skipped when the file is imported.

# %%
show("04_name_main/greet.py")
run("greet.py", "04_name_main")

# %%
show("04_name_main/main.py")
run("main.py", "04_name_main")

# %% [markdown]
# The `print` at the top of `greet.py` runs both times, because everything
# outside the block runs on import. The block itself runs only when
# `greet.py` is the file you ran.
#
# ### Why the course's modules end this way
#
# A `pull_` module in this course does two jobs. As a script, it pulls data
# from a vendor and saves it, and that is how `dodo.py` runs it. As a module,
# it offers a `load_` function that reads what the pull saved, and that is how
# a notebook uses it. Here is the shape of the FedWatch case study's
# `pull_fed_funds_futures.py`, shortened:
#
# ```python
# def pull_fed_funds_futures(start_date=START_DATE, end_date=END_DATE):
#     """Pull daily ZQ bars from Databento."""      # goes out to the network
#     ...
#
#
# def load_fed_funds_futures(data_dir=DATA_DIR):
#     """Load the cached ZQ daily bars pulled by this module."""
#     return pd.read_parquet(Path(data_dir) / PARQUET_NAME)
#
#
# if __name__ == "__main__":
#     df = pull_fed_funds_futures()
#     df.to_parquet(DATA_DIR / PARQUET_NAME)
# ```
#
# `dodo.py` runs `python ./src/pull_fed_funds_futures.py`, so `__name__` is
# `"__main__"` and the pull runs. The guide notebook runs
# `import pull_fed_funds_futures` and calls `load_fed_funds_futures()`, so the
# block is skipped and nothing touches the network. Without the guard, every
# import of the module, by a notebook, a test, or another module, would pull
# the data again.
#
# The block has a second common use: a quick check of a module by hand.
# `paths.py` in the install example prints the paths it computes when you run
# it, and prints nothing when it is imported:

# %%
run("src/myproj/paths.py", "../project_paths/install_approach")

# %% [markdown]
# ## What to remember
#
# - A file is a module, and a folder with an `__init__.py` is a package.
#   `sys.path` decides which one an `import` finds.
# - An installed package can be imported from anywhere, which is how code is
#   shared between projects.
# - Code under `if __name__ == "__main__":` runs when the file is run, not
#   when it is imported. In this course, that block is where a `pull_` module
#   does its pulling.
