"""Path utilities anchored on package location.

This module provides functions that return paths relative to the project root.
The key insight: by installing the package in editable mode, __file__ provides
a stable anchor point that works regardless of where you run your code from.
"""

from pathlib import Path


def project_root() -> Path:
    """Return the project root directory.

    The calculation: paths.py -> myproj/ -> src/ -> project_root/
    That's 3 levels up, so parents[2] (0-indexed).
    """
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    """Return the _data directory."""
    return project_root() / "_data"


def data_path(*parts: str) -> Path:
    """Return a path within the _data directory.

    Examples:
        data_path()                      -> /path/to/project/_data
        data_path("raw")                 -> /path/to/project/_data/raw
        data_path("raw", "prices.csv")   -> /path/to/project/_data/raw/prices.csv
    """
    return data_dir().joinpath(*parts)


def output_dir() -> Path:
    """Return the _output directory."""
    return project_root() / "_output"


def output_path(*parts: str) -> Path:
    """Return a path within the _output directory.

    Examples:
        output_path()                    -> /path/to/project/_output
        output_path("charts")            -> /path/to/project/_output/charts
        output_path("charts", "fig.png") -> /path/to/project/_output/charts/fig.png
    """
    return output_dir().joinpath(*parts)


if __name__ == "__main__":
    # Quick test when run directly
    print(f"Project root: {project_root()}")
    print(f"Data dir:     {data_dir()}")
    print(f"Output dir:   {output_dir()}")
