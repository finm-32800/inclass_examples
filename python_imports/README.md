# Python Imports and Packages

This directory contains progressive examples teaching how Python imports work: modules, packages, and common pitfalls.

## Examples

| Directory | Topic |
|-----------|-------|
| `01_simple_module` | Import a single `.py` file as a module |
| `02_package_directory` | Import a directory with `__init__.py` as a package |
| `03_name_shadowing` | How local files can shadow installed packages (`sys.path` ordering) |
| `04_name_main` | What `if __name__ == "__main__":` does: a module that is also a script |

Work through them in order. The notebook
[`01_modules_and_packages_ipynb.py`](01_modules_and_packages_ipynb.py) runs all
four, adds the installable package in
[`../project_paths/install_approach/`](../project_paths/install_approach/), and
is published in the course textbook. Its executed copy,
`01_modules_and_packages_ipynb.ipynb`, is rebuilt from the repository root with
`doit run_notebooks:01_modules_and_packages_ipynb`.
